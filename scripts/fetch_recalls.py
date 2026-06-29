import requests
import pandas as pd
import time
import os

discover_url = "https://api.nhtsa.gov/products/vehicle/models"
recalls_url = "https://api.nhtsa.gov/recalls/recallsByVehicle"

years = range(2015, 2025)   # 2015–2024

all_records = []

for year in years:
    # 第一步:问 NHTSA 这一年有哪些特斯拉车型(召回口径 issueType=r)
    d = requests.get(discover_url,
                     params={"make": "Tesla", "modelYear": str(year), "issueType": "r"},
                     timeout=30)
    models_raw = [m.get("model") for m in d.json().get("results", [])]
    models = sorted(set(models_raw))
    print(f"=== {year} 年发现 {len(models)} 个车型: {models}")

    # 第二步:照着真实车型名,逐个抓召回
    for model in models:
        params = {"make": "Tesla", "model": model, "modelYear": str(year)}
        try:
            r = requests.get(recalls_url, params=params, timeout=30)
            results = r.json().get("results", [])
            for rec in results:
                rec["query_model"] = model
                rec["query_year"] = year
                all_records.append(rec)
            print(f"    {model} {year}: {len(results)} 条")
        except Exception as e:
            print(f"    {model} {year}: 出错 -> {e}")
        time.sleep(0.3)

# 去重:同一个召回(NHTSACampaignNumber)会在多个车型变体下重复出现
df = pd.DataFrame(all_records)
before = len(df)
if "NHTSACampaignNumber" in df.columns:
    df = df.drop_duplicates(subset="NHTSACampaignNumber", keep="first")
after = len(df)

os.makedirs("data/raw", exist_ok=True)
out_path = "data/raw/tesla_recalls_raw.csv"
df.to_csv(out_path, index=False, encoding="utf-8-sig")

print("-" * 50)
print(f"去重前: {before} 条,去重后: {after} 条")
print(f"已保存到: {out_path}")