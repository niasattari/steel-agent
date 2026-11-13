import duckdb
con = duckdb.connect("steel.duckdb", read_only=True)
print(con.sql("""
    SELECT COUNT(*) AS total_pairs,
           COUNT(e.value_usd) AS comparable,
           COUNT(*) FILTER (WHERE e.value_usd IS NULL) AS missing,
           COUNT(*) FILTER (WHERE e.value_usd IS NOT NULL
               AND ABS(100*(i.value_usd - e.value_usd)/e.value_usd) > 100) AS gap_over_100pct,
           COUNT(*) FILTER (WHERE e.value_usd IS NOT NULL
               AND ABS(15*(i.value_usd - e.value_usd)/e.value_usd) <= 100) AS gap_within_100pct
    FROM trade i LEFT JOIN trade e
      ON i.year=e.year AND i.hs_code=e.hs_code
     AND e.reporter='Rep. of Korea' AND e.partner='Germany' AND e.flow='export'
    WHERE i.reporter='Germany' AND i.partner='Rep. of Korea' AND i.flow='import'
""").df())
