import duckdb
con = duckdb.connect("steel.duckdb", read_only=True)
print(con.sql("""
    WITH i AS (SELECT year, partner, SUM(value_usd) v FROM trade
               WHERE reporter='Germany' AND flow='import' AND partner IN ('India','Türkiye')
               GROUP BY year, partner),
         e AS (SELECT year, reporter AS partner, SUM(value_usd) v FROM trade
               WHERE partner='Germany' AND flow='export' AND reporter IN ('India','Türkiye')
               GROUP BY year, reporter)
    SELECT i.year, i.partner, ROUND(i.v/1e6, 1) AS imp_usd_m, ROUND(e.v/1e6, 1) AS exp_usd_m,
           ROUND(100*(i.v - e.v)/e.v) AS gap_pct
    FROM i JOIN e USING (year, partner)
    ORDER BY partner, year
""").df())
