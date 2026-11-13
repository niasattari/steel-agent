import os
import json
import duckdb
import anthropic
from dotenv import load_dotenv

load_dotenv()  # reads ANTHROPIC_API_KEY from .env
con = duckdb.connect("steel.duckdb", read_only=True)
client = anthropic.Anthropic()          # reads ANTHROPIC_API_KEY
MODEL = "claude-sonnet-5-5"

SYSTEM = """You are a trade-data analyst for a steel and metals consulting team.
Data: table trade(year, reporter, partner, flow, hs_code, qty_kg, value_usd, cifvalue, fobvalue)
from UN Comtrade. flow is 'import' or 'export'. HS 7208-7212 = flat-rolled steel.
Focal country Germany; partners: China, India, Türkiye, Italy, Rep. of Korea.
Rules:
- Never quote numbers from memory. Query the data first.
- Run find_mirror_gaps before explaining any trend involving a partner.
- Convert kg to tonnes; price per tonne = value_usd / (qty_kg / 1000).
- Imports are CIF-valued and exports FOB-valued, so gaps under about 15% are normal.
- Qty values can be estimated by Comtrade; mention this as a caveat.
- If data is missing or contradictory, say so. Do not guess causes.
- Do all arithmetic (shares, ratios, percentage changes) in SQL, never in your head.
Answer format: Key finding (2-3 sentences), Numbers (short table), Data caveats.
- Any count, or claim using "only", "all" or "none", must come from a SQL query, not from counting by hand.
- Define the mirror gap as (German import - partner export) / partner export, and use it consistently.
- If a tool result looks truncated, say so and query the data directly.
- Never state how many year/product pairs, rows or years meet a condition unless a COUNT query
     in this conversation returned that number. If you did not run one, do not state a count.
- Describe patterns only (what differs, by how much, in which direction). Do not interpret them
  with words like "noise", "error", "misreporting" or "suggests" unless a cited source says so.
  - When ranking, state explicitly whether the full order or only the top entry is the same on another data source.
- When two sources disagree, say they disagree. Never call one side "unreliable" or "wrong" unless a tool result shows which one is."""


def run_sql(query: str) -> str:
    if not query.strip().lower().startswith(("select", "with")):
        return "Only SELECT queries are allowed."
    try:
        return con.execute(query).df().head(50).to_string()
    except Exception as e:
        return f"SQL error: {e}"


def find_mirror_gaps(hs_code: str = None, min_gap_pct: float = 30, partner: str = None) -> str:
    q = """
    SELECT i.year, i.partner AS exporter, i.hs_code,
           ROUND(i.qty_kg/1000) AS imp_tonnes, ROUND(e.qty_kg/1000) AS exp_tonnes,
           ROUND(i.value_usd) AS imp_usd, ROUND(e.value_usd) AS exp_usd,
           ROUND(100*(i.value_usd - e.value_usd)/NULLIF(e.value_usd,0)) AS gap_pct
    FROM trade i LEFT JOIN trade e
      ON i.year=e.year AND i.hs_code=e.hs_code
     AND i.partner=e.reporter AND e.partner=i.reporter AND e.flow='export'
    WHERE i.flow='import'
      AND (? IS NULL OR CAST(i.hs_code AS VARCHAR) = ?)
      AND (? IS NULL OR i.partner = ?)
      AND (e.value_usd IS NULL OR ABS(100*(i.value_usd - e.value_usd)/NULLIF(e.value_usd,0)) > ?)
    ORDER BY i.partner, i.hs_code, i.year LIMIT 300"""
    try:
        df = con.execute(q, [hs_code, hs_code, partner,
                         partner, min_gap_pct]).df()
        return df.to_string() if len(df) else "No gaps above threshold."
    except Exception as e:
        return f"Error: {e}"


TOOLS = {"run_sql": run_sql, "find_mirror_gaps": find_mirror_gaps}
TOOL_SCHEMAS = [
    {"name": "run_sql",
     "description": "Run a read-only DuckDB SQL SELECT on table trade(year, reporter, partner, flow, hs_code, qty_kg, value_usd, cifvalue, fobvalue). Returns up to 50 rows.",
     "input_schema": {"type": "object",
                      "properties": {"query": {"type": "string"}},
                      "required": ["query"]}},
    {"name": "find_mirror_gaps",
     "description": "Compare Germany's reported imports with each partner's reported exports to Germany. Returns rows where the partner's export is missing or differs from the import by more than min_gap_pct percent.",
     "input_schema": {"type": "object",
                      "properties": {
                          "hs_code": {"type": "string", "description": "Optional, e.g. '7209'"},
                          "min_gap_pct": {"type": "number"},
                          "partner": {"type": "string", "description": "Optional, e.g. 'Rep. of Korea'"}}}},
]


def agent(question: str, max_steps: int = 8):
    messages = [{"role": "user", "content": question}]
    trace, tin, tout = [], 0, 0
    for _ in range(max_steps):
        r = client.messages.create(model=MODEL, max_tokens=2000, system=SYSTEM,
                                   tools=TOOL_SCHEMAS, messages=messages)
        tin += r.usage.input_tokens
        tout += r.usage.output_tokens
        messages.append({"role": "assistant", "content": r.content})
        if r.stop_reason != "tool_use":
            text = "".join(b.text for b in r.content if b.type == "text")
            return text, trace, (tin, tout)
        results = []
        for b in r.content:
            if b.type == "tool_use":
                out = str(TOOLS[b.name](**b.input))
                trace.append({"tool": b.name, "input": b.input, "output": out})
                results.append(
                    {"type": "tool_result", "tool_use_id": b.id, "content": out})
        messages.append({"role": "user", "content": results})
    return "Stopped: too many steps.", trace, (tin, tout)


if __name__ == "__main__":
    text, trace, usage = agent(input("Question: "))
    print(text)
