import pandas as pd
import os

df = pd.read_csv("data/raw/tesla_recalls_raw.csv")
print("清洗前:", df.shape)

# ---------- 1. 统一车型名 ----------
def clean_model(name):
    s = str(name).upper()
    if "CYBERTRUCK" in s: return "Cybertruck"
    if "SEMI" in s:       return "Semi"
    if "MODEL 3" in s:    return "Model 3"
    if "MODEL Y" in s:    return "Model Y"
    if "MODEL S" in s:    return "Model S"
    if "MODEL X" in s:    return "Model X"
    return name

df["model_clean"] = df["query_model"].apply(clean_model)

# ---------- 2. 解析召回日期(召回是 日/月/年,跟投诉相反!) ----------
df["recall_date"] = pd.to_datetime(df["ReportReceivedDate"], format="%d/%m/%Y", errors="coerce")

# ---------- 3. 拆解 Component(冒号分层,取第一段作主系统) ----------
df["Component"] = df["Component"].fillna("UNKNOWN")
df["component_main"] = df["Component"].str.split(":").str[0].str.strip()

# ---------- 4. 保存召回级干净表 ----------
keep = ["NHTSACampaignNumber", "model_clean", "query_year", "recall_date",
        "component_main", "Component", "Summary", "Consequence", "Remedy"]
keep = [c for c in keep if c in df.columns]
recalls_clean = df[keep].copy()

os.makedirs("data/processed", exist_ok=True)
recalls_clean.to_csv("data/processed/recalls_clean.csv", index=False, encoding="utf-8-sig")
print("已保存召回级表:", recalls_clean.shape, "-> data/processed/recalls_clean.csv")

print("-" * 50)
print("召回条数(应=60):", len(recalls_clean))
print("日期解析成功数:", recalls_clean["recall_date"].notna().sum())
print()
print("各主系统的召回数:")
print(recalls_clean["component_main"].value_counts())