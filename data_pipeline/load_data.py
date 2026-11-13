import duckdb
import pandas as pd

df = pd.read_csv("comtrade.csv")

# Rename to the schema the agent will use
df = df.rename(columns={
    "refYear": "year", "reporterDesc": "reporter", "partnerDesc": "partner",
    "cmdCode": "hs_code", "netWgt": "qty_kg", "primaryValue": "value_usd"})
df["flow"] = df["flowCode"].map({"M": "import", "X": "export"})
df = df[["year", "reporter", "partner", "flow", "hs_code",
         "qty_kg", "value_usd", "cifvalue", "fobvalue"]]

con = duckdb.connect("steel.duckdb")
con.execute("CREATE OR REPLACE TABLE trade AS SELECT * FROM df")

# Check 1: which South Korea export rows are missing?
print(con.sql("""
    SELECT year, hs_code FROM trade
    WHERE reporter = 'Rep. of Korea' AND flow = 'export'
    ORDER BY year, hs_code
""").df())

# Check 2: rows per reporter/partner/flow
print(con.sql("""
    SELECT reporter, partner, flow, COUNT(*) AS n
    FROM trade GROUP BY ALL ORDER BY reporter, partner, flow
""").df())

# Check 3: nulls or zeros in the key columns
print(con.sql("""
    SELECT COUNT(*) FILTER (WHERE qty_kg IS NULL OR qty_kg = 0) AS missing_qty,
           COUNT(*) FILTER (WHERE value_usd IS NULL OR value_usd = 0) AS missing_value
    FROM trade
""").df())
