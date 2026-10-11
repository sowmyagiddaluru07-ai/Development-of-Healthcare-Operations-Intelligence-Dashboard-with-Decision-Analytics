# 🏥 Medical Operations Intelligence (MOI) Dashboard & Automation System

An enterprise-grade healthcare operational intelligence, predictive analytics, and automated decision-support platform built for **Infosys Internship**.

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/)
[![Database](https://img.shields.io/badge/Database-MongoDB%20Atlas-green.svg)](https://www.mongodb.com/cloud/atlas)
[![Dashboard](https://img.shields.io/badge/Dashboard-Streamlit-red.svg)](https://streamlit.io/)
[![Status](https://img.shields.io/badge/Tests-34%2F34%20Passing-brightgreen.svg)]()

---

## 🎯 Executive Overview

The **Medical Operations Intelligence System** consolidates healthcare data from 15 operational collections across 4 hospital facilities and 10 clinical departments into MongoDB Atlas. The platform transforms raw data into:

- **Executive Operations Dashboard**: 14 key operational KPIs & dynamic Operational Health Score (0-100%).
- **Domain Analytics**: Patient flow, doctor productivity, revenue collections, claim denial aging, pharmacy stockouts, ER triage, and quality metrics.
- **Machine Learning Layer**: Ridge Regression 30-day patient volume forecaster, Random Forest appointment no-show predictor, and Isolation Forest anomaly detector.
- **Rule Automation Engine**: Automated capacity, wait time, inventory stockout, and payment aging alert checks.
- **AI Operations Copilot**: Natural Language Q&A over live MongoDB aggregations & automated daily executive briefings.
- **Reporting & Business Intelligence**: Export engines for Power BI CSVs, multi-sheet Excel workbooks, and ReportLab PDF executive reports.

---

## 🛠️ Technology Stack

- **Backend / Core**: Python 3.9+
- **Database**: MongoDB Atlas / Local MongoDB (PyMongo driver with Connection Pooling)
- **Frontend / UI**: Streamlit 1.30+ & Plotly Dark Theme
- **Data Engineering & Analytics**: Pandas 2.0+, NumPy
- **Machine Learning**: Scikit-Learn 1.4+ (Ridge, RandomForestClassifier, IsolationForest)
- **Reporting & BI**: ReportLab (PDFs), OpenPyXL (Excel), Power BI Integration (CSV Exports & DAX Measures)
- **Configuration**: python-dotenv (Zero hardcoded credentials)

---

## 📂 Project Architecture

```text
Medical-Operations-Intelligence/
├── app.py                             # Main Streamlit application entry point
├── run_project.py                     # Master one-click initialization & launcher
├── requirements.txt                   # Complete project dependencies
├── README.md                          # Project documentation & sitemap
├── TESTING.md                         # Complete testing protocol & test run instructions
├── .env.example                       # Environment configuration template
├── .gitignore                         # Version control exclusions
│
├── config/                            # Environment & central settings
├── database/                          # Connection pooling, indexing & safe non-destructive seeding
├── data/                              # Synthetic data generator (50,000+ realistic records)
├── analytics/                         # MongoDB Aggregation Pipeline engines (KPI, Patient, Staff, Revenue, Claims, Ops)
├── ml/                                # Forecasting, No-Show prediction, Anomaly detection & Model Manager
├── automation/                        # Automated alert rules engine & audit logger
├── copilot/                           # Natural Language Q&A assistant & executive briefing engine
├── dashboard/                         # 12 Streamlit dashboard pages & dark theme components
├── powerbi/                           # Power BI CSV exports, DAX measures & documentation
├── reports/                           # PDF Executive ReportLab generator & Excel exporter
├── docs/                              # Architecture, User Guide, Internship Report, Presentation & Viva prep
└── tests/                             # Automated test suite (34/34 passing)
```

---

## 🚀 Quick Setup & Execution (Windows / VS Code)

### Prerequisites
1. Installed **Python 3.9+** or **`uv`**.
2. Active MongoDB instance (MongoDB Atlas cluster URI or local MongoDB `mongodb://localhost:27017`).

### 1-Step Automatic Execution
Clone or open the workspace directory in VS Code / PowerShell and run:

```powershell
uv run python run_project.py
```

`run_project.py` performs the complete multi-stage pipeline automatically:
1. Loads `.env` configuration.
2. Establishes MongoDB connection & creates 15 collections with background multi-field indexes.
3. Performs **safe non-destructive seeding** (skips existing populated collections, seeds missing ones).
4. Trains ML models (Volume Forecaster, No-Show Predictor, Anomaly Detector).
5. Executes automated operational alert rule evaluations.
6. Exports Power BI CSV data tables to `powerbi/exports/`.
7. Logs system initialization in MongoDB audit logs.
8. Launches the Streamlit Dashboard at **`http://localhost:8501`**.

---

## 📊 Dashboard Sitemap (12 Pages)

| Page | Description | Key Features |
|---|---|---|
| **Executive Dashboard** | High-level Operational Health Score & KPIs | Gauge chart, 14 executive KPIs, daily/monthly trends, facility benchmark charts |
| **Patient Operations** | Flow & Admissions | Admissions, status breakdown pie chart, wait time by dept, demographics |
| **Staff Intelligence** | Workforce Productivity | Headcount summary, doctor productivity, utilization by role, overtime alerts |
| **Revenue Intelligence** | Financial Performance | Total revenue, collection rate, daily/monthly collections, payment method, AR aging |
| **Insurance Claims** | Denial Management | Claim volume, denial reasons pie chart, payer comparison bar chart, claim aging |
| **Pharmacy** | Inventory SKUs | Low-stock alert table, category valuation bar chart, vendor ratings |
| **Laboratory** | SLA & Turnaround Times | Test volume, SLA turnaround time by test category, abnormal result tracking |
| **Emergency** | ER Triage & Waiting Times | Triage Level 1-5 distribution, wait times, critical cases count, disposition |
| **Quality & Experience**| NPS & Patient Feedback | Satisfaction gauge, NPS score, feedback sentiment pie chart, quality incident logs |
| **AI Predictions** | Machine Learning Insights | 30-day demand forecast line chart, high-risk no-shows, Isolation Forest anomalies |
| **Alerts** | Rule Automation Engine | Active operational alerts table, severity breakdown, one-click resolution actions |
| **Copilot** | AI Assistant & Briefings | Natural Language Q&A over MongoDB, automated daily executive briefing generator |

---

## 🧪 Running Tests

To execute the automated unit test suite:

```powershell
uv run python -m unittest discover tests
```

Expected Output: `Ran 34 tests in ~25s -> OK (100% Pass Rate)`.

---

## 📄 Documentation Sitemap

- [System Architecture](docs/system_architecture.md)
- [User Manual](docs/user_guide.md)
- [Testing Protocol](TESTING.md)
- [Internship Report](docs/INTERNSHIP_REPORT.md)
- [15-Slide Presentation with Speaker Notes](docs/INTERNSHIP_PRESENTATION.md)
- [Viva Preparation Guide](docs/VIVA_PREPARATION.md)

---

© 2026 Medical Operations Intelligence — Infosys Internship Project.
