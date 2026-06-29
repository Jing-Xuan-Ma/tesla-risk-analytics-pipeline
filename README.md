# Tesla Vehicle Quality & Risk Analytics Pipeline

An end-to-end data pipeline that turns public **NHTSA** vehicle complaint and recall
records into **actuarial-style quality-risk indicators** for Tesla vehicles, surfaced
through an interactive Tableau dashboard.

**Stack:** Python · MySQL · SQL · NHTSA API · Tableau · Apache Airflow *(in progress)*

**🔗 Live dashboard:** [Tesla Vehicle Quality & Risk Analytics on Tableau Public](https://public.tableau.com/app/profile/jingxuan.ma8760/viz/TeslaVehicleQualityRiskAnalytics/1)

---

## Overview

Car owners file complaints with the U.S. National Highway Traffic Safety
Administration (NHTSA); manufacturers and regulators issue formal recalls. This
project automatically extracts both signals, cleans and stores them in a relational
database, and quantifies vehicle quality risk using a **frequency × severity**
framework borrowed from insurance loss modeling.

The goal is twofold:

1. **A product** — a reproducible risk-monitoring dataset and metric layer that ranks
   the riskiest *model × component* combinations and measures how long a problem takes
   to go from first complaint to official recall.
2. **A demonstration** — an end-to-end workflow spanning data extraction, data quality
   engineering, relational modeling, analytical SQL, and BI visualization.

## The actuarial angle (core differentiator)

The central metric mirrors the way insurers estimate expected loss:

```
Expected loss (insurance)  =  claim frequency  ×  claim severity
Quality risk   (this repo) =  complaint freq.  ×  defect severity
```

- **Frequency** — how often a *model × component* is complained about.
- **Severity** — how dangerous those complaints are, weighted by outcome.
- **Risk score** — the two combined, so a rare-but-deadly issue is not buried under a
  common-but-minor one.

## Data sources

| Source | NHTSA endpoint | Records (deduplicated) |
| --- | --- | --- |
| Complaints | `complaints/complaintsByVehicle` | **11,349** |
| Recalls | `recalls/recallsByVehicle` | **60** |

Coverage: Tesla **Model 3 / S / X / Y** (plus **Cybertruck** and **Semi** where
present), model years **2015–2024**.

## Pipeline

```
NHTSA API
   │  extract  (Python · requests)          dynamic model discovery + dedup
   ▼
Raw CSV  (data/raw/)
   │  transform  (Python · pandas)          date parsing, component explosion,
   ▼                                         model-name normalization
Clean CSV  (data/processed/)
   │  load  (SQLAlchemy · PyMySQL)
   ▼
MySQL  (tesla_risk)
   │  analyze  (SQL)                         frequency × severity, recall lag
   ▼
Tableau dashboard
```

## Data engineering highlights

These are the non-obvious problems the pipeline solves:

- **Dynamic model discovery.** NHTSA stores Tesla models under many inconsistent names
  per year (`MODEL Y`, `MODEL Y 5-SEAT`, `MODEL Y (All Variants)`, …). Instead of
  hard-coding names, the extractor first queries NHTSA for the *actual* models recorded
  each year, then pulls complaints against those names — so nothing is silently missed.
- **Deduplication by stable IDs.** Because models are split into variants, the same
  event is returned multiple times. Complaints are deduplicated on `odiNumber`
  (**30,777 → 11,349**) and recalls on `NHTSACampaignNumber` (**227 → 60**), so counts
  reflect real distinct events.
- **Date-format discovery.** The two endpoints use *different* date formats: complaints
  are `MM/DD/YYYY`, recalls are `DD/MM/YYYY`. Each is parsed with an explicit format to
  avoid silent mis-parsing of the recall-lag metric.
- **Multi-component handling.** A complaint can name several components
  (`STEERING,ENGINE`); these are exploded into one row per component
  (**11,349 → 17,854** component-level rows) for accurate component-level frequency,
  while complaint-level counts are preserved separately.

## Dashboard

The interactive Tableau dashboard presents two views:

1. **Top 15 components by quality risk score** (frequency × severity) — forward
   collision avoidance, vehicle speed control, and electrical systems lead.
2. **Average recall lag by model** — days from first complaint to official recall.

[**View it live on Tableau Public →**](https://public.tableau.com/app/profile/jingxuan.ma8760/viz/TeslaVehicleQualityRiskAnalytics/1)

## Key findings

### Recall lag — first complaint to official recall

Of 60 recalls, **54 (90%)** could be matched to prior complaints by *model +
component*.

| Metric | Value |
| --- | --- |
| Mean lag | ~1,396 days (≈ 3.8 years) |
| Median lag | 1,258 days (≈ 3.4 years) |
| Longest lag | 3,147 days (≈ 8.6 years) — Model S air bags, 50 prior complaints |

| Model | Avg. recall lag (days) |
| --- | --- |
| Model X | 2,294 |
| Model S | 1,950 |
| Model 3 | 1,497 |
| Model Y | 369 |
| Cybertruck | 275 |

Older lines (S/X) accumulate problems and recall slowly; newer lines (Y/Cybertruck)
show shorter observed lags.

### Frequency vs. severity — two different kinds of risk

| Model × component | Frequency | Avg. severity |
| --- | --- | --- |
| Forward Collision Avoidance (Model Y) | 1,717 | 2.07 |
| Forward Collision Avoidance (Model 3) | 1,666 | 1.27 |
| Electrical System (Model Y) | 437 | **4.44** |

The most-complained system (forward collision avoidance) is **high-frequency but
lower-severity**, while the electrical system is **lower-frequency but the most
severe** — exactly the distinction the frequency/severity framework is designed to
surface.

## Severity scoring

Each complaint receives a severity score:

```
severity = 1 (base) + fire×5 + crash×3 + injuries×2 + deaths×10
```

These weights encode expert/engineering judgment about relative harm. They are a
**tunable parameter**; a production actuarial model would calibrate them against
historical loss data.

## Repository structure

```
tesla-risk-analytics-pipeline/
├── scripts/
│   ├── extract.py              # complaints: discover models, extract, dedup
│   ├── fetch_recalls.py        # recalls: same pattern
│   ├── transform_complaints.py # clean dates/models, explode components
│   ├── transform_recalls.py    # clean dates/models, split component hierarchy
│   ├── recall_lag.py           # first-complaint -> recall lag
│   ├── load_to_mysql.py        # load clean tables into MySQL
│   ├── prep_tableau.py         # build Tableau-ready summary tables
│   ├── check_data.py           # data-health inspection
│   └── diagnose.py             # NHTSA model-name diagnostics
├── sql/
│   └── risk_metrics.sql        # frequency × severity + recall-lag queries
├── data/
│   ├── raw/                    # untouched API pulls
│   ├── processed/              # cleaned, analysis-ready tables
│   └── tableau/                # summary tables feeding the dashboard
└── README.md
```

## How to reproduce

**1. Environment**

```bash
python -m venv venv
venv\Scripts\activate          # Windows  (source venv/bin/activate on macOS/Linux)
pip install requests pandas sqlalchemy pymysql python-dotenv
```

**2. Database** — in MySQL:

```sql
CREATE DATABASE tesla_risk;
```

Create a `.env` file in the project root (never committed):

```
DB_PASSWORD=your_mysql_password
```

**3. Run the pipeline**

```bash
python scripts/extract.py
python scripts/fetch_recalls.py
python scripts/transform_complaints.py
python scripts/transform_recalls.py
python scripts/recall_lag.py
python scripts/load_to_mysql.py
python scripts/prep_tableau.py
```

**4. Analyze** — run `sql/risk_metrics.sql` in MySQL Workbench, or open the published
Tableau dashboard linked above.

## Roadmap

- [x] Extraction (complaints + recalls) with dynamic discovery and deduplication
- [x] Cleaning / transformation (dates, components, model normalization)
- [x] Load into MySQL
- [x] Recall-lag analysis
- [x] Frequency × severity risk metrics in SQL
- [x] Tableau dashboard — component risk + recall lag ([live link](https://public.tableau.com/app/profile/jingxuan.ma8760/viz/TeslaVehicleQualityRiskAnalytics/1)) · geographic map pending data enrichment
- [ ] Apache Airflow orchestration for scheduled, automated runs

## Notes

All data is sourced from the public NHTSA API and contains no personal information.
Severity weights and risk definitions reflect the modeling choices documented above
and are intended for analytical demonstration.
