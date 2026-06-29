import pandas as pd

complaints = pd.read_csv("data/processed/complaints_by_component.csv", parse_dates=["complaint_date"])
recalls = pd.read_csv("data/processed/recalls_clean.csv", parse_dates=["recall_date"])

# 投诉的零件统一成大写,方便和召回的主系统对齐
complaints["component"] = complaints["component"].astype(str).str.upper().str.strip()
recalls["component_main"] = recalls["component_main"].astype(str).str.upper().str.strip()

results = []

# 对每一个召回,找它“召回日期之前、同车型同系统”的最早投诉
for _, rc in recalls.iterrows():
    model = rc["model_clean"]
    comp = rc["component_main"]
    rdate = rc["recall_date"]
    if pd.isna(rdate):
        continue

    # 筛选:同车型 + 同系统 + 投诉日期早于召回日期
    mask = (
        (complaints["model_clean"] == model)
        & (complaints["component"] == comp)
        & (complaints["complaint_date"] < rdate)
    )
    matched = complaints[mask]

    if len(matched) > 0:
        first_complaint = matched["complaint_date"].min()
        lag_days = (rdate - first_complaint).days
        results.append({
            "campaign": rc["NHTSACampaignNumber"],
            "model": model,
            "component": comp,
            "first_complaint_date": first_complaint.date(),
            "recall_date": rdate.date(),
            "lag_days": lag_days,
            "n_prior_complaints": len(matched),
        })

lag_df = pd.DataFrame(results)
lag_df.to_csv("data/processed/recall_lag.csv", index=False, encoding="utf-8-sig")

print("能匹配到先行投诉的召回数:", len(lag_df), "/ 60")
print("已保存 -> data/processed/recall_lag.csv")
print("-" * 50)

if len(lag_df) > 0:
    print("平均 lag(天):", round(lag_df["lag_days"].mean(), 1))
    print("中位数 lag(天):", int(lag_df["lag_days"].median()))
    print("最短 / 最长:", lag_df["lag_days"].min(), "/", lag_df["lag_days"].max())
    print()
    print("按车型平均 lag:")
    print(lag_df.groupby("model")["lag_days"].mean().round(1).sort_values(ascending=False))
    print()
    print("lag 最长的 5 个召回:")
    print(lag_df.sort_values("lag_days", ascending=False)
              [["model", "component", "lag_days", "n_prior_complaints"]].head().to_string(index=False))