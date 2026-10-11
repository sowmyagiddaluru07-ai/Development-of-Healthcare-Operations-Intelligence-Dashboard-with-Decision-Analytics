# 📊 INFOSYS INTERNSHIP PRESENTATION
## Medical Operations Intelligence (MOI) Dashboard & Automation System

---

## Slide 1: Title & Introduction
**Title:** Medical Operations Intelligence (MOI) Dashboard & Automation System  
**Subtitle:** Enterprise Healthcare Analytics, Predictive ML & Automated Decision Control Tower  
**Presenter:** Infosys Intern  
**Domain:** Healthcare Data Engineering & Full-Stack AI Solutions  

> **Speaker Notes:**  
> Good morning respected evaluators and mentors. Today I am presenting my Infosys internship project: the Medical Operations Intelligence Dashboard & Automation System. This platform consolidates hospital operational data into MongoDB Atlas and transforms it into real-time dashboards, predictive ML indicators, automated alerts, and natural language executive briefings.

---

## Slide 2: Project Background & Problem Statement
- **Healthcare Data Siloes:** Modern hospitals operate separate systems for admissions, billing, pharmacy, lab, and staffing.
- **Lack of Visibility:** Executive management struggles to get real-time visibility into bed capacity, patient bottlenecks, and revenue leakage.
- **Manual Reporting:** Current operational tracking relies on delayed weekly static reports.

> **Speaker Notes:**  
> In healthcare administration, delayed operational visibility can lead to overcrowded emergency rooms, delayed lab turnaround times, stockout of life-saving medications, and high insurance claim denial rates. My project solves this by creating a real-time operational control tower.

---

## Slide 3: Objectives & Key Deliverables
1. **Centralized Data Lake:** Store 15 operational healthcare collections in MongoDB Atlas.
2. **Interactive UI:** 12 Streamlit dashboard pages with dark-theme Plotly visualizations.
3. **Executive Health Index:** Weighted Operational Health Score (0-100%).
4. **Machine Learning Layer:** Patient demand forecasting, no-show prediction, and anomaly detection.
5. **Rule Automation:** Automated capacity, wait time, inventory, and AR alerts.
6. **AI Copilot:** Natural language query processor over MongoDB.

> **Speaker Notes:**  
> We established six clear deliverables. The platform does not attempt clinical diagnosis; instead, it focuses purely on operational efficiency, financial performance, workforce productivity, and compliance risk.

---

## Slide 4: System Architecture
- **Layer 1: User Interface** — Streamlit 1.30+ with Plotly charts & custom CSS glassmorphism.
- **Layer 2: Analytics Engine** — Optimized MongoDB aggregation pipelines (`$match`, `$group`, `$lookup`).
- **Layer 3: Machine Learning & Automation** — Scikit-Learn (Ridge Regression, Random Forest, Isolation Forest).
- **Layer 4: Database & Ingestion** — MongoDB Atlas, PyMongo connection pooling, background indexes.
- **Layer 5: BI & Reporting** — Power BI CSV exports, ReportLab PDF summaries, OpenPyXL Excel workbooks.

> **Speaker Notes:**  
> As shown in the architecture diagram, the platform follows a decoupled multi-tier architecture. All database credentials are managed via environment variables to guarantee enterprise security.

---

## Slide 5: MongoDB Schema & Collection Architecture
- **15 Primary Collections:** `patients`, `staff`, `appointments`, `admissions`, `billing`, `insurance_claims`, `medical_coding`, `pharmacy_inventory`, `laboratory_tests`, `emergency_cases`, `quality_incidents`, `patient_feedback`, `vendors`, `purchase_orders`, `financial_transactions`.
- **Relational Integrity:** Valid foreign key linkage across Patient IDs (`PAT...`), Staff IDs (`STF...`), Facilities (`FAC001-004`), and Departments (`DEP001-010`).

> **Speaker Notes:**  
> MongoDB Atlas serves as our primary database. We created multi-field background indexes on foreign keys and date fields to ensure sub-second aggregation query execution even over large datasets.

---

## Slide 6: Safe Non-Destructive Seeding System
- **Data Safety Principle:** Database seeder checks collection document counts before inserting.
- **Zero Automated Wipes:** Existing data is preserved automatically unless an explicit `--force` reset is passed.
- **Synthetic Volume:** Generates 50,000+ realistic cross-referenced documents covering 6 months of historical data.

> **Speaker Notes:**  
> Data safety is critical. Our database seeder evaluates record counts and skips populated collections, preventing unintentional data wipes during system restarts.

---

## Slide 7: Executive Dashboard & Operational Health Score
- **Operational Health Score:** Single dynamic score (0-100%) computed from weighted operational metrics (wait time, bed occupancy, staff utilization, claim denials, NPS).
- **14 Executive KPIs:** Total Revenue, Billed vs Paid, No-Show Rate, Average Wait Time, Bed Occupancy, CSAT.

> **Speaker Notes:**  
> The Executive Dashboard features a prominent Plotly gauge chart displaying the hospital's overall Operational Health Score, giving executives an instantaneous health check of the entire hospital network.

---

## Slide 8: Patient Flow & Staff Intelligence
- **Patient Operations:** Analyzes appointment status distributions, waiting time by department, length of stay, and age/gender demographics.
- **Staff Intelligence:** Measures doctor productivity (appointments processed), workforce utilization by role, shift coverage, and overtime burnout risks.

> **Speaker Notes:**  
> The Staff Intelligence module tracks provider productivity and nurse-to-patient ratios. Automated overtime alerts highlight clinical staff members working over 10 overtime hours per week.

---

## Slide 9: Revenue Intelligence & Insurance Claims
- **Revenue Analytics:** Tracks total billed revenue, collected revenue, payment method share, and AR aging buckets (0-30, 31-60, 61-90, 90+ days).
- **Insurance Claims:** Evaluates claim denial rates by payer and breaks down root causes (coding errors, eligibility, documentation).

> **Speaker Notes:**  
> Claim denials represent significant financial leakage for hospitals. Our claims analytics module isolates top denial reasons and compares payer performance, allowing revenue teams to target appeal efforts.

---

## Slide 10: Pharmacy, Laboratory & Emergency Intelligence
- **Pharmacy:** Low stock alert table (items below reorder levels), stock valuation by category, vendor delivery reliability.
- **Laboratory:** Test volume, turnaround time (TAT) SLA compliance, abnormal result tracking.
- **Emergency:** ER triage severity distribution (Level 1-5), triage-to-doctor waiting times, admission disposition.

> **Speaker Notes:**  
> Operations managers can track pharmacy SKUs approaching stockout and monitor laboratory test turnaround times against target SLAs.

---

## Slide 11: Machine Learning — Patient Volume Demand Forecasting
- **Algorithm:** Ridge Regression with temporal feature engineering (`day_of_week`, `day_of_month`, `month`, `is_weekend`, `week_of_year`).
- **Output:** 30-day daily patient volume forecast with upper and lower confidence bounds.
- **Evaluation Metrics:** MAE, RMSE, and R² metrics computed on test split.

> **Speaker Notes:**  
> Our ML forecasting engine uses Ridge Regression to predict daily patient volume for the next 30 days. This allows hospital managers to proactively adjust staffing and bed availability.

---

## Slide 12: Machine Learning — No-Show Prediction & Anomaly Detection
- **No-Show Predictor:** Random Forest Classifier (100 estimators) calculating appointment no-show probability and feature importance rankings.
- **Anomaly Detection:** Isolation Forest algorithm detecting statistical outliers in waiting times, volume spikes, and revenue anomalies.

> **Speaker Notes:**  
> The Random Forest model identifies scheduled appointments with a high risk of no-show, enabling automated SMS reminders. Isolation Forest flags operational anomalies automatically.

---

## Slide 13: Rule Automation Engine & AI Copilot
- **Alert Engine:** Automated background checks for capacity limits, long wait times, inventory stockouts, and claim denial spikes.
- **AI Copilot:** Natural Language Q&A assistant querying live MongoDB aggregations and generating automated daily executive briefings.

> **Speaker Notes:**  
> The AI Copilot translates plain English queries into MongoDB aggregation pipelines, providing instant operational answers without requiring technical SQL/MongoDB knowledge.

---

## Slide 14: Reporting & Business Intelligence Exports
- **Power BI Engine:** Exports clean CSV datasets to `powerbi/exports/` accompanied by complete DAX measures documentation.
- **PDF Executive Reports:** ReportLab PDF report generator creating formatted multi-page executive summaries.
- **Excel Workbooks:** Multi-sheet Excel workbook export via OpenPyXL.

> **Speaker Notes:**  
> The platform seamlessly integrates with external BI tools like Power BI Desktop, enabling hospital analysts to build custom executive dashboards.

---

## Slide 15: Verification, Conclusion & Q&A
- **Unit Test Suite:** 34/34 passing unit tests (100% pass rate).
- **Execution Command:** `uv run python run_project.py`
- **Dashboard URL:** `http://localhost:8501`

> **Speaker Notes:**  
> In conclusion, the Medical Operations Intelligence system is fully built, tested, and verified. Thank you for your guidance throughout this internship. I am now open to your questions.
