# Agent testing log (Steel Trade Analyst)

Method: ran each example question in the app, checked the numbers against my own SQL
(verify.py, verify_questions.py, check_*.py), fixed the agent, reran.

| # | Question | Result | Problem found | Fix |
|---|----------|--------|---------------|-----|
| 1 | China imports 2021-2024 | Numbers matched | Computed shares in its head, contradicted itself | Rule: all arithmetic in SQL |
| 2 | South Korea inconsistencies | Numbers matched | Miscounted pairs (twice); mirror-gap tool cut off at 60 rows, hiding Korea; interpretive wording ("noise") | Raised row limit, added partner filter, rule: counts only from a COUNT query, no interpretation |
| 3 | Highest price per tonne 2023 | Numbers matched | "Ranking is the same" only true for the top entry; called China's data "unreliable" without evidence | Rules: state whether full order matches; never name one side wrong |
| 4 | India vs Türkiye over time | Numbers matched (incl. 12 mirror gaps) | Ambiguous wording about when prices fell | Noted only |

Known limitations
- Korea's 2023 gap (+122%) compares 5 products against 4 (7209 missing on the export side).
  Excluding 7209: about +42% value.
- Cause of the mirror gaps is not known; the agent is built not to guess.
- Spot-checked one cell against the Comtrade website (China exports to Germany, HS 7210, 2023): exact match.