# 🎓 INFOSYS INTERNSHIP PROJECT REPORT

## Project Title: Medical Operations Intelligence (MOI) Dashboard & Automation System
**Domain:** Healthcare Data Engineering, Operational Intelligence & Machine Learning  
**Author:** Infosys Intern  
**Date:** October 2026  

---

## Executive Summary

Healthcare organizations manage complex operational workflows involving patient admissions, clinical staff scheduling, revenue cycles, insurance claims, pharmacy inventory, laboratory test turnaround times, emergency department triage, and patient experience metrics. Legacy hospital information systems store data in siloes, making it challenging for management to gain real-time visibility into bottlenecks, revenue loss, stockouts, or operational risks.

The **Medical Operations Intelligence (MOI)** platform is an enterprise-grade operational intelligence, predictive analytics, and automated decision-support system. Built using **Python**, **MongoDB Atlas**, **Streamlit**, **Plotly**, and **Scikit-Learn**, the platform consolidates data from 15 operational collections across 4 hospital facilities and 10 clinical departments.

---

## 1. Problem Statement & Objectives

### Problem Statement
Hospital administrators lack a unified operational control tower to monitor real-time hospital performance, workforce utilization, claim denial risks, inventory stockouts, emergency wait times, and financial health. Existing tools rely on manual static spreadsheets or delayed weekly reporting.

### Core Objectives
1. **Unified Data Integration**: Consolidate healthcare operational data into a scalable MongoDB Atlas database.
2. **Real-Time KPI Dashboards**: Render an interactive Streamlit UI with 14 executive KPIs and an automated **Operational Health Score (0-100%)**.
3. **Predictive Machine Learning**: Implement ML models for 30-day patient volume forecasting (Ridge Regression), appointment no-show prediction (Random Forest), and operational anomaly detection (Isolation Forest).
4. **Automated Alert System**: Build a rule detection engine to flag capacity breaches, long wait times, low inventory, and claim denial spikes.
5. **AI Operations Copilot**: Develop a Natural Language Q&A assistant to query MongoDB aggregations and generate automated daily executive briefings.
6. **Business Intelligence Export**: Provide automated export pipelines for Power BI CSVs, multi-tab Excel workbooks, and ReportLab PDF executive summaries.

---

## 2. System Architecture & Multi-Tier Design

The MOI platform employs a decoupled 5-tier architecture:

```text
+-----------------------------------------------------------------------+
|                         Streamlit UI Layer                            |
| (12 Interactive Pages, Sidebar Filters, Dark Glassmorphic Design)     |
+-----------------------------------+-----------------------------------+
                                    |
+-----------------------------------v-----------------------------------+
|                     Analytics & Intelligence Layer                    |
| (KPI Engine, Patient, Staff, Revenue, Claims, Operational Analytics)  |
+-----------------------------------+-----------------------------------+
                                    |
+-----------------------------------v-----------------------------------+
|               Machine Learning & AI Automation Layer                  |
| (Ridge Forecaster, RandomForest No-Show, Isolation Forest Anomalies) |
+-----------------------------------+-----------------------------------+
                                    |
+-----------------------------------v-----------------------------------+
|                   Database & Data Ingestion Layer                     |
| (MongoDB Atlas / Local, Connection Pool, Safe Non-Destructive Seeder) |
+-----------------------------------+-----------------------------------+
                                    |
+-----------------------------------v-----------------------------------+
|                External Exports & Integrations Layer                  |
|   (Power BI CSV Engine, ReportLab PDF Generator, Excel Workbooks)     |
+-----------------------------------------------------------------------+
```

---

## 3. Database Schema & MongoDB Collections

The system creates 15 primary operational collections with background multi-field indexing:

1. **`patients`**: Demographics, age groups, insurance status, contact details, facility assignment.
2. **`staff`**: Doctors, nurses, technicians, admin staff, hourly rates, overtime hours, utilization rates.
3. **`appointments`**: Scheduled time, actual start time, waiting time, appointment type, status (`Completed`, `Scheduled`, `Cancelled`, `No-show`).
4. **`admissions`**: Admission/discharge dates, bed numbers, length of stay (LOS), readmission tracking.
5. **`billing`**: Net amounts, discounts, tax, payment status (`Paid`, `Partial`, `Pending`, `Overdue`), payment methods, outstanding AR.
6. **`insurance_claims`**: Payer details, claim amounts, approval/denial status, denial reasons, claim age.
7. **`medical_coding`**: ICD/CPT codes, coding accuracy, documentation completeness.
8. **`pharmacy_inventory`**: SKU stock quantities, reorder levels, unit prices, expiry dates, daily consumption.
9. **`laboratory_tests`**: Test categories, turnaround times (TAT), status, abnormal flags.
10. **`emergency_cases`**: Arrival timestamps, triage levels (1-5), waiting times, admission disposition.
11. **`quality_incidents`**: Incident types, severity, resolution days, SOP adherence.
12. **`patient_feedback`**: Ratings (1-5), NPS scores, sentiment classification (`Positive`, `Neutral`, `Negative`).
13. **`vendors`**: Vendor ratings, delivery reliability scores, contract dates.
14. **`purchase_orders`**: PO order dates, expected/actual delivery dates, total amounts.
15. **`financial_transactions`**: Revenue vs expense line items, budget comparisons.

---

## 4. Key Modules & Technical Implementation

### A. Non-Destructive Database Seeder (`database/seed.py`)
- Evaluates existing collection record counts.
- Skips already populated collections to guarantee zero data loss.
- Seeds only missing collections unless `--force` reset flag is explicitly provided.

### B. Machine Learning Engine (`ml/`)
- **Patient Volume Forecaster (`ml/forecasting.py`)**: Uses Ridge Regression with temporal feature engineering (`day_of_week`, `is_weekend`, `month`, `week_of_year`) to predict daily appointment demand for the next 30 days. Computes MAE, RMSE, and R² evaluation metrics.
- **No-Show Predictor (`ml/no_show_prediction.py`)**: Employs a RandomForestClassifier (100 estimators) trained on appointment type, department, day of week, hour, and waiting time to calculate no-show risk probabilities. Computes Accuracy, Precision, Recall, F1, and ROC-AUC.
- **Anomaly Detector (`ml/anomaly_detection.py`)**: Implements Isolation Forest to flag operational outliers in waiting times, patient volume surges, and revenue discrepancies.

### C. AI Operations Copilot (`copilot/`)
- Parses natural language user queries regarding revenue, delays, doctor productivity, claims, bed occupancy, pharmacy stock, and emergency cases.
- Executes real-time MongoDB aggregations to return structured answers and JSON response payloads without fabricating data.

---

## 5. Verification & Testing Results

The automated test suite (`tests/test_project.py`) comprises **34 unit tests** covering configuration, data generation, MongoDB aggregations, ML training, automated rule checks, copilot Q&A, and Power BI exports.

**Test Run Output:**
```text
Ran 34 tests in 25.102s
OK (34/34 Passed - 100% Success Rate)
```

---

## 6. Project Impact & Conclusion

The **Medical Operations Intelligence** platform successfully demonstrates end-to-end full-stack software development, data engineering, machine learning integration, and UI/UX design. It empowers healthcare leaders to make data-driven operational decisions, optimize resource allocation, prevent financial leakage, and improve patient care quality.
