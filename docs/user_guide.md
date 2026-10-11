# User Guide & Operational Manual

## Medical Operations Intelligence (MOI)

Welcome to the **Medical Operations Intelligence** dashboard. This platform provides real-time operational insights, machine learning predictions, and rule-based automation across your healthcare facilities.

---

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.9+
- MongoDB instance (MongoDB Atlas cluster or local MongoDB service)

### 2. Environment Setup
Create a `.env` file in the project root:
```env
MONGODB_URI=mongodb+srv://<username>:<password>@cluster.mongodb.net/?retryWrites=true&w=majority
DATABASE_NAME=medical_operations_db
STREAMLIT_SERVER_PORT=8501
DEBUG=True
```

### 3. Running the Entire System (One Command)
Execute the master project runner:
```bash
python run_project.py
```

This master script automatically:
1. Validates configuration settings.
2. Connects to MongoDB & creates 15 collections with optimized indexes.
3. Generates 50,000+ realistic synthetic healthcare documents & seeds the database.
4. Trains ML models (Volume Forecaster, No-Show Predictor, Anomaly Detector).
5. Runs automated operational alert checks.
6. Exports Power BI CSV data tables.
7. Launches the interactive Streamlit dashboard at `http://localhost:8501`.

---

## 🖥️ Dashboard Navigation

The left sidebar provides access to 12 operational views and filters:

1. **Executive Dashboard**: High-level Operational Health Score gauge, 14 executive KPIs, and daily/monthly trends.
2. **Patient Operations**: Admissions, appointment status distribution, wait times, and patient demographics.
3. **Staff Intelligence**: Workforce headcount, doctor productivity scorecards, utilization, and overtime alerts.
4. **Revenue Intelligence**: Total revenue, collection rate, payment method breakdown, and AR aging buckets.
5. **Insurance Claims**: Claim submission volume, denial rate breakdown by reason, and payer benchmarking.
6. **Pharmacy**: Stock levels, low stock alerts, stock value by category, and vendor performance.
7. **Laboratory**: Test volume, turnaround time (TAT) SLA compliance, and abnormal result tracking.
8. **Emergency**: Triage level distribution, wait times, critical cases count, and admission disposition.
9. **Quality & Experience**: Patient satisfaction (NPS/CSAT), sentiment analysis, and quality incident logs.
10. **AI Predictions**: 30-day demand forecast, high-risk no-show patient lists, and anomaly detection.
11. **Alerts**: Active rule-based operational alerts with resolution actions.
12. **Copilot**: Natural Language Q&A assistant and automated daily executive briefings.

---

## 📊 Power BI & Report Generation

- **Power BI Integration**: Generated CSV datasets are saved automatically to `powerbi/exports/`. Connect Power BI Desktop to these files to refresh external dashboards.
- **PDF Executive Reports**: Generated using `reports/pdf_generator.py`.
- **Excel Data Workbooks**: Generated using `reports/excel_exporter.py`.
