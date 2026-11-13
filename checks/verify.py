import duckdb
con = duckdb.connect("steel.duckdb", read_only=True)
print(con.sql("""
WITH i AS (SELECT year, SUM(qty_kg)/1000 t, SUM(value_usd) usd FROM trade
           WHERE reporter='Germany' AND partner='China' AND flow='import' GROUP BY year),
     x AS (SELECT year, SUM(qty_kg)/1000 t, SUM(value_usd) usd FROM trade
           WHERE reporter='China' AND partner='Germany' AND flow='export' GROUP BY year)
SELECT i.year, ROUND(i.t) imp_t, ROUND(x.t) exp_t, ROUND(100*x.t/i.t,1) share_t_pct,
       ROUND(i.usd/1e6,1) imp_usd_m, ROUND(x.usd/1e6,1) exp_usd_m,
       ROUND(100*x.usd/i.usd,1) share_usd_pct
FROM i JOIN x USING (year) ORDER BY year
""").df())
