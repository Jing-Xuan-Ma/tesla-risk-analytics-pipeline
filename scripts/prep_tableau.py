import pandas as pd
import os

os.makedirs("data/tableau", exist_ok=True)

# ========== 表1:零件级风险(给"零件风险"图用)==========
comp = pd.read_csv("data/processed/complaints_by_component.csv")

comp["severity"] = (1
                    + comp["is_fire"].astype(int) * 5
                    + comp["is_crash"].astype(int) * 3
                    + comp["injuries"] * 2
                    + comp["deaths"] * 10)

risk = (comp.groupby(["model_clean", "component"])
        .agg(frequency=("odiNumber", "count"),
             risk_score=("severity", "sum"),
             avg_severity=("severity", "mean"))
        .reset_index())
risk["avg_severity"] = risk["avg_severity"].round(2)

risk = risk[~risk["component"].str.contains("UNKNOWN", case=False, na=False)]
risk = risk.sort_values("risk_score", ascending=False)

risk.to_csv("data/tableau/risk_by_component.csv", index=False, encoding="utf-8-sig")
print("表1 已生成 risk_by_component.csv:", risk.shape)

# ========== 表2:召回滞后(给"召回滞后"图用)==========
lag = pd.read_csv("data/processed/recall_lag.csv")
lag_summary = (lag.groupby("model")
               .agg(n_recalls=("campaign", "count"),
                    avg_lag_days=("lag_days", "mean"),
                    max_lag_days=("lag_days", "max"))
               .reset_index())
lag_summary["avg_lag_days"] = lag_summary["avg_lag_days"].round(1)
lag_summary = lag_summary.sort_values("avg_lag_days", ascending=False)

lag_summary.to_csv("data/tableau/recall_lag_by_model.csv", index=False, encoding="utf-8-sig")
print("表2 已生成 recall_lag_by_model.csv:", lag_summary.shape)

lag.to_csv("data/tableau/recall_lag_detail.csv", index=False, encoding="utf-8-sig")
print("明细版 已生成 recall_lag_detail.csv:", lag.shape)

print("-" * 40)
print("三张表都在 data/tableau/ 文件夹")