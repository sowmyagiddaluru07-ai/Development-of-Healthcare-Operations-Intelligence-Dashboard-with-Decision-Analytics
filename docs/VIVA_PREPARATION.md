# 💬 VIVA PREPARATION GUIDE
## Medical Operations Intelligence (MOI) System

This guide prepares you for common technical and conceptual viva questions asked during your internship project defense.

---

## 1. General & High-Level Questions

### Q1: What is the main objective of your project?
**Answer:** The Medical Operations Intelligence (MOI) System is an operational analytics and automated decision-support platform for hospital management. It consolidates healthcare operational data from multiple departments into MongoDB Atlas and transforms it into 12 real-time Streamlit dashboards, machine learning forecasts, automated alert triggers, and an AI Operations Copilot. It is strictly an operational management tool, not a clinical diagnosis system.

### Q2: Why did you choose MongoDB Atlas instead of a Relational Database (SQL)?
**Answer:** Healthcare operational data comes from diverse departments (patients, staff, pharmacy SKUs, lab tests, claims, billing) with flexible and nested document structures (e.g., patient demographics, contact info, claim aging history). MongoDB Atlas provides flexible JSON document schema, high-throughput MongoDB aggregation pipelines (`$match`, `$group`, `$lookup`), scalability, and cloud Atlas availability.

---

## 2. Technical Architecture & Data Engineering

### Q3: How do you handle database credentials securely?
**Answer:** Database credentials are never hardcoded in source code or documentation. All sensitive configurations (e.g., `MONGODB_URI`) are loaded from an environment file (`.env`) using `python-dotenv`. `.env` is listed in `.gitignore` so secrets are never committed to version control.

### Q4: How does your database seeding system prevent accidental data loss?
**Answer:** The database seeder (`database/seed.py`) is built on a non-destructive safety principle. Before inserting synthetic data, it checks document counts for each collection. If a collection already contains data, it skips seeding for that collection. It only clears or re-seeds collections if an explicit `--force` reset flag is passed.

---

## 3. Machine Learning & Predictive Analytics

### Q5: What machine learning models are implemented in your project?
**Answer:**
1. **Patient Volume Demand Forecast:** Ridge Regression model trained on temporal features (`day_of_week`, `day_of_month`, `month`, `is_weekend`, `week_of_year`) to predict daily appointment demand for the next 30 days. Evaluated using MAE, RMSE, and R².
2. **No-Show Risk Predictor:** Random Forest Classifier (100 estimators) trained on appointment type, department, day of week, hour, and waiting time to calculate the probability that a scheduled appointment will result in a no-show. Evaluated using Accuracy, Precision, Recall, F1, and ROC-AUC.
3. **Anomaly Detection:** Isolation Forest algorithm detecting statistical outliers in daily waiting times, appointment volume spikes, and billing revenue discrepancies.

---

## 4. Automation & AI Copilot

### Q6: How does the Operational Alert Engine work?
**Answer:** The alert engine (`automation/alert_engine.py`) runs automated rule checks against MongoDB collections based on predefined operational thresholds (e.g., bed occupancy > 85%, average wait time > 45 minutes, low pharmacy stock below reorder levels, overdue bills > 60 days). When a threshold is breached, an active alert card is logged in the `operational_alerts` collection and rendered on the Alerts dashboard page with interactive resolution controls.

### Q7: How does the AI Operations Copilot answer user questions?
**Answer:** The AI Operations Copilot (`copilot/query_engine.py`) parses natural language query keywords (e.g., "revenue", "wait time", "claims", "bed occupancy", "doctor productivity"). It converts the user's intent into live MongoDB aggregation pipelines over actual project data, returning structured text summaries and JSON data payloads without inventing numbers.

---

## 5. Demonstration & Commands

### Q8: How do you launch the application?
**Answer:** From VS Code or PowerShell terminal, run:
```powershell
uv run python run_project.py
```
This script validates settings, connects to MongoDB, initializes collections and indexes, performs non-destructive seeding, trains ML models, runs alert checks, exports Power BI CSVs, and opens the Streamlit dashboard at `http://localhost:8501`.

### Q9: How do you run the automated tests?
**Answer:** Run:
```powershell
uv run python -m unittest discover tests
```
All 34 automated unit tests pass with 100% success rate.
