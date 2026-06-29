-- ================================================================
-- Tesla 车辆质量风险指标 (frequency × severity)
-- 数据库: tesla_risk
-- 框架: 精算式 frequency-severity 损失分析
-- ================================================================

USE tesla_risk;

-- ---------- 指标 1:风险评分排名(frequency × severity) ----------
-- 每条投诉严重度 = 基础1 + 起火×5 + 碰撞×3 + 伤×2 + 亡×10
SELECT
    model_clean,
    component,
    COUNT(*) AS frequency,
    SUM(1 + is_fire*5 + is_crash*3 + injuries*2 + deaths*10) AS risk_score,
    ROUND(AVG(1 + is_fire*5 + is_crash*3 + injuries*2 + deaths*10), 2) AS avg_severity
FROM complaints_by_component
GROUP BY model_clean, component
ORDER BY risk_score DESC
LIMIT 20;

-- ---------- 指标 2:排除 UNKNOWN/OTHER 的清晰版 ----------
-- 去掉信息量低的兜底分类,聚焦明确零件
SELECT
    model_clean,
    component,
    COUNT(*) AS frequency,
    SUM(1 + is_fire*5 + is_crash*3 + injuries*2 + deaths*10) AS risk_score,
    ROUND(AVG(1 + is_fire*5 + is_crash*3 + injuries*2 + deaths*10), 2) AS avg_severity
FROM complaints_by_component
WHERE component NOT LIKE '%UNKNOWN%'
GROUP BY model_clean, component
ORDER BY risk_score DESC
LIMIT 20;

-- ---------- 指标 3:按车型的召回滞后 (recall lag) ----------
-- 数据来自 recall_lag 表(投诉首次出现到官方召回的天数)
SELECT
    model,
    COUNT(*) AS n_recalls,
    ROUND(AVG(lag_days), 1) AS avg_lag_days,
    MAX(lag_days) AS max_lag_days
FROM recall_lag
GROUP BY model
ORDER BY avg_lag_days DESC;