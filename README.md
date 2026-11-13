# Steel Trade Analyst Agent

An agent that answers plain-English questions about Germany's flat-rolled steel trade
(HS 7208-7212) using UN Comtrade data. It writes SQL against a local database, compares
Germany's reported imports with each partner's reported exports (mirror data), and flags
inconsistencies. It is instructed to describe patterns only and never to state a cause.

## Data
- UN Comtrade, annual, 2019-2024
- Germany and 5 partners: China, India, Türkiye, Italy, Rep. of Korea
- Both sides of each flow: Germany's imports and the partner's exports to Germany
- 296 rows in DuckDB (steel.duckdb)

## How it works
- agent.py: Claude with two tools, run_sql (read-only SELECT) and find_mirror_gaps
- app.py: Streamlit interface showing the answer, every SQL step, and the token cost
- Rules in the system prompt: query before quoting numbers, do all arithmetic in SQL,
  counts only from a COUNT query, no interpretation of causes

## Run
1. Create .env with ANTHROPIC_API_KEY=...
2. streamlit run app.py

Rebuild the data: python data_pipeline/download_data.py, then python data_pipeline/load_data.py
(needs COMTRADE_KEY in .env). Run all scripts from this folder.

## Testing
testing_log.md: four example questions, each checked against my own SQL (checks/).
One cell was also spot-checked against the Comtrade website (exact match).

## Known limitations
- The cause of the large mirror gaps is not known, and the agent does not guess.
- Korea's gap for 2023 compares 5 products on the import side with 4 on the export side.
- Quantities in Comtrade can be estimated, so price per tonne is indicative.
- Tested on 4 questions only. Answers should be reviewed by an analyst.

## Next steps
- Web search for possible explanations of gaps, with cited sources
- More partners and years, and a returned-rows flag instead of threshold-only gap output
- Human review step before anything goes to a client