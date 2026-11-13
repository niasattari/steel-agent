
import duckdb
con = duckdb.connect("steel.duckdb", read_only=True)
print(con.sql("""
    SELECT year, reporter, partner, flow, hs_code,
           ROUND(qty_kg/1000) AS tonnes, ROUND(value_usd) AS usd
    FROM trade
    WHERE hs_code = '7210' AND year = 2023
      AND ((reporter='China' AND partner='Germany' AND flow='export')
        OR (reporter='Germany' AND partner='China' AND flow='import'))
""").df())
