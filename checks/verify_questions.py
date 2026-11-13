import duckdb
con = duckdb.connect("steel.duckdb", read_only=True)

print("Q3: average import price per tonne by partner, 2023 (weighted)")
print(con.sql("""
    SELECT partner, ROUND(SUM(qty_kg)/1000) AS tonnes,
           ROUND(SUM(value_usd)/(SUM(qty_kg)/1000)) AS usd_per_tonne
    FROM trade
    WHERE reporter='Germany' AND flow='import' AND year=2023
    GROUP BY partner ORDER BY usd_per_tonne DESC
""").df())

print("\nQ4: India and Türkiye imports by year")
print(con.sql("""
    SELECT year, partner, ROUND(SUM(qty_kg)/1000) AS tonnes,
           ROUND(SUM(value_usd)/1e6, 1) AS usd_m,
           ROUND(SUM(value_usd)/(SUM(qty_kg)/1000)) AS usd_per_tonne
    FROM trade
    WHERE reporter='Germany' AND flow='import' AND partner IN ('India','Türkiye')
    GROUP BY year, partner ORDER BY partner, year
""").df())

print("\nQ2: South Korea mirror comparison, all products, by year")
print(con.sql("""
    SELECT i.year, i.hs_code, ROUND(i.qty_kg/1000) AS imp_t, ROUND(e.qty_kg/1000) AS exp_t,
           ROUND(i.value_usd) AS imp_usd, ROUND(e.value_usd) AS exp_usd
    FROM trade i LEFT JOIN trade e
      ON i.year=e.year AND i.hs_code=e.hs_code
     AND e.reporter='Rep. of Korea' AND e.partner='Germany' AND e.flow='export'
    WHERE i.reporter='Germany' AND i.partner='Rep. of Korea' AND i.flow='import'
    ORDER BY i.hs_code, i.year
""").df().to_string())
