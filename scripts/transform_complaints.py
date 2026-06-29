import pandas as pd
import os

df = pd.read_csv("data/raw/tesla_complaints_raw.csv")
print("清洗前:", df.shape)

# ---------- 1. 统一车型名(把变体归并成干净车型) ----------
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

# ---------- 2. 解析日期(文本 -> 真正的日期类型) ----------
# 原格式是 日/月/年,如 08/05/2025 -> dayfirst=True
df["incident_date"]  = pd.to_datetime(df["dateOfIncident"], format="%m/%d/%Y", errors="coerce")
df["complaint_date"] = pd.to_datetime(df["dateComplaintFiled"], format="%m/%d/%Y", errors="coerce")
# ---------- 3. 统一严重度字段(布尔/数值规范化) ----------
df["is_crash"]  = df["crash"].astype(str).str.upper().eq("TRUE")
df["is_fire"]   = df["fire"].astype(str).str.upper().eq("TRUE")
df["injuries"]  = pd.to_numeric(df["numberOfInjuries"], errors="coerce").fillna(0).astype(int)
df["deaths"]    = pd.to_numeric(df["numberOfDeaths"], errors="coerce").fillna(0).astype(int)

# ---------- 4. 保存“投诉级”干净表(一行一条投诉,11349 条不变) ----------
keep = ["odiNumber", "model_clean", "query_year", "incident_date", "complaint_date",
        "is_crash", "is_fire", "injuries", "deaths", "components", "summary"]
keep = [c for c in keep if c in df.columns]
complaint_level = df[keep].copy()

os.makedirs("data/processed", exist_ok=True)
complaint_level.to_csv("data/processed/complaints_clean.csv", index=False, encoding="utf-8-sig")
print("已保存投诉级表:", complaint_level.shape, "-> data/processed/complaints_clean.csv")

# ---------- 5. 拆解零件,生成“投诉-零件级”表(一行一个零件) ----------
df["components"] = df["components"].fillna("UNKNOWN")
# 按逗号拆,去掉首尾空格,炸成多行
df["component_list"] = df["components"].str.split(",")
exploded = df.explode("component_list")
exploded["component"] = exploded["component_list"].str.strip()

keep2 = ["odiNumber", "model_clean", "query_year", "complaint_date",
         "is_crash", "is_fire", "injuries", "deaths", "component"]
keep2 = [c for c in keep2 if c in exploded.columns]
component_level = exploded[keep2].copy()

component_level.to_csv("data/processed/complaints_by_component.csv", index=False, encoding="utf-8-sig")
print("已保存投诉-零件级表:", component_level.shape, "-> data/processed/complaints_by_component.csv")

print("-" * 50)
print("投诉级行数(应=11349):", len(complaint_level))
print("零件级行数(应 > 11349):", len(component_level))