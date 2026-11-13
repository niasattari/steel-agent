import duckdb
con = duckdb.connect("steel.duckdb", read_only=True)
print(con.sql("""
    SELECT year, reporter, flow, ROUND(qty_kg/1000) AS tonnes, ROUND(value_usd) AS usd
    FROM trade
    WHERE hs_code = '7212' AND year IN (2021, 2024)
      AND ((reporter='Germany' AND partner='China' AND flow='import')
        OR (reporter='China' AND partner='Germany' AND flow='export'))
    ORDER BY year, flow
""").df())
