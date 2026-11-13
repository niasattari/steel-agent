import duckdb
con = duckdb.connect("steel.duckdb", read_only=True)
print(con.sql("""
    SELECT partner, ROUND(SUM(qty_kg)/1000) AS imp_t,
           ROUND(SUM(value_usd)/(SUM(qty_kg)/1000)) AS imp_usd_t
    FROM trade WHERE reporter='Germany' AND flow='import' AND year=2023
    GROUP BY partner ORDER BY imp_usd_t DESC
""").df())
print(con.sql("""
    SELECT reporter AS partner, ROUND(SUM(qty_kg)/1000) AS exp_t,
           ROUND(SUM(value_usd)/(SUM(qty_kg)/1000)) AS exp_usd_t, COUNT(*) AS n_products
    FROM trade WHERE partner='Germany' AND flow='export' AND year=2023
    GROUP BY reporter ORDER BY exp_usd_t DESC
""").df())
print(con.sql("""
    SELECT hs_code, ROUND(SUM(qty_kg)/1000) AS t, ROUND(SUM(value_usd)/(SUM(qty_kg)/1000)) AS usd_t
    FROM trade WHERE reporter='Germany' AND flow='import' AND year=2023 AND partner='China'
    GROUP BY hs_code ORDER BY hs_code
""").df())
