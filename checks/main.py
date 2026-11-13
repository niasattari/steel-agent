import os
import time
import requests
import pandas as pd

URL = "https://comtradeapi.un.org/data/v1/get/C/A/HS"
HEADERS = {"Ocp-Apim-Subscription-Key": os.environ["COMTRADE_KEY"]}
GERMANY = "276"
PARTNERS = {"China": "156", "India": "699", "Turkey": "792",
            "Italy": "380", "South Korea": "410"}

queries = []
for code in PARTNERS.values():
    queries.append((GERMANY, code, "M"))   # Germany's imports from partner
    queries.append((code, GERMANY, "X"))   # partner's exports to Germany

rows = []
for reporter, partner, flow in queries:
    r = requests.get(URL, headers=HEADERS, params={
        "reporterCode": reporter, "partnerCode": partner, "flowCode": flow,
        "period": "2019,2020,2021,2022,2023,2024",
        "cmdCode": "7208,7209,7210,7211,7212",
        "partner2Code": "0", "motCode": "0", "customsCode": "C00",
        "includeDesc": "true"})
    r.raise_for_status()
    data = r.json()["data"]
    print(reporter, "->", partner, flow, ":", len(data), "rows")
    rows += data
    time.sleep(2)

df = pd.DataFrame(rows)[["refYear", "reporterCode", "reporterDesc", "partnerCode",
                         "partnerDesc", "flowCode", "cmdCode", "netWgt",
                         "primaryValue", "cifvalue", "fobvalue"]]
df.to_csv("comtrade.csv", index=False)
print(df.shape)
