import requests

# NHTSA 的"发现"接口:列出某品牌某年份实际收录了哪些车型
url = "https://api.nhtsa.gov/products/vehicle/models"

for year in [2020, 2021, 2022, 2023, 2024]:
    params = {"make": "Tesla", "modelYear": str(year), "issueType": "c"}
    r = requests.get(url, params=params, timeout=30)
    print(f"--- {year} 年 (状态码 {r.status_code}) ---")
    if r.status_code == 200:
        results = r.json().get("results", [])
        names = [m.get("model") for m in results]
        print("NHTSA 实际收录的特斯拉车型:", names)
    else:
        print("返回内容:", r.text[:300])
    print()
    