import pandas as pd

pd.set_option("display.max_columns", None)
pd.set_option("display.width", 200)

df = pd.read_csv("data/raw/tesla_complaints_raw.csv")

print("表格大小:", df.shape, "  (行数, 列数)")
print()

print("所有列名:")
print(list(df.columns))
print()

print("各车型投诉数:")
print(df["query_model"].value_counts())
print()

print("各年份投诉数:")
print(df["query_year"].value_counts().sort_index())
print()

# 只挑关键列看样本,避免 summary 长文本刷屏
key_cols = ["odiNumber", "query_model", "query_year", "crash", "fire",
            "numberOfInjuries", "numberOfDeaths", "components",
            "dateOfIncident", "dateComplaintFiled"]
exist = [c for c in key_cols if c in df.columns]
print("前 5 条样本(关键列):")
print(df[exist].head())