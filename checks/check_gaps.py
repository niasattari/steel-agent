import duckdb

con = duckdb.connect("steel.duckdb")

print(con.sql("""
    SELECT year, flow, reporter, partner, hs_code, qty_kg, value_usd
    FROM trade
    WHERE hs_code = '7209'
      AND ((reporter = 'Germany' AND partner = 'Rep. of Korea')
        OR (reporter = 'Rep. of Korea' AND partner = 'Germany'))
    ORDER BY year, flow
""").df())

print(con.sql("""
    SELECT COUNT(*) FILTER (WHERE qty_kg IS NULL OR qty_kg = 0) AS missing_qty,
           COUNT(*) FILTER (WHERE value_usd IS NULL OR value_usd = 0) AS missing_value
    FROM trade
""").df())
