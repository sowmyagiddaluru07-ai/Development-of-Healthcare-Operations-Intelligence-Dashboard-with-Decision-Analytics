# System Architecture & Technical Specifications

## Medical Operations Intelligence (MOI) System

### 1. Architectural Overview
The Medical Operations Intelligence platform is an enterprise multi-facility healthcare analytics system built on a modular 5-tier architecture:

```
+-----------------------------------------------------------------------+
|                         Streamlit UI Layer                            |
| (Executive Dashboard, 12 Domain Pages, Responsive Filters, Components)|
+-----------------------------------+-----------------------------------+
                                    |
+-----------------------------------v-----------------------------------+
|                     Analytics & Intelligence Layer                    |
| (KPI Engine, Patient/Staff/Revenue/Claims/Operational Analytics)     |
+-----------------------------------+-----------------------------------+
                                    |
+-----------------------------------v-----------------------------------+
|               Machine Learning & AI Automation Layer                  |
| (Ridge Forecaster, RandomForest No-Show, Isolation Forest Anomalies) |
+-----------------------------------+-----------------------------------+
                                    |
+-----------------------------------v-----------------------------------+
|                   Database & Data Ingestion Layer                     |
|  (MongoDB Atlas / Local, PyMongo Aggregations, Synthetic Generator)   |
+-----------------------------------+-----------------------------------+
                                    |
+-----------------------------------v-----------------------------------+
|                External Exports & Integrations Layer                  |
|   (Power BI CSV Engine, ReportLab PDF Generator, Excel Workbooks)     |
+-----------------------------------------------------------------------+
```

### 2. Core Modules & Data Pipeline
1. **Data Ingestion & Seeding (`data/generators.py`, `database/seed.py`)**:
   - Generates realistic cross-referenced synthetic datasets across 15 MongoDB collections:
     - Patients (5,000+)
     - Appointments (12,000+)
     - Admissions (5,000+)
     - Staff (120+)
     - Billing & Invoices (8,000+)
     - Insurance Claims (5,000+)
     - Medical Coding (3,000+)
     - Pharmacy Inventory (250 SKUs)
     - Laboratory Tests (6,000+)
     - Emergency Cases (2,500+)
     - Quality Incidents (600+)
     - Patient Feedback (3,500+)
     - Vendors (30+)
     - Purchase Orders (1,200+)
     - Financial Transactions (6,000+)

2. **MongoDB Database Architecture (`database/connection.py`, `database/initialization.py`)**:
   - Singleton connection manager with connection pooling and automated retry.
   - Background multi-field indexing on foreign keys (`patient_id`, `facility_id`, `department_id`) and timestamp fields (`appointment_date`, `created_at`) for high-throughput aggregation queries.

3. **Analytics Pipeline (`analytics/`)**:
   - **KPI Engine**: Aggregates 14 executive KPIs and calculates dynamic Operational Health Score (0-100%).
   - **Domain Analytics**: Optimized MongoDB aggregation pipelines (`$match`, `$group`, `$lookup`, `$project`, `$facet`) handling real-time filtering by facility, department, and time periods.

4. **Machine Learning Engines (`ml/`)**:
   - **Patient Volume Forecasting (`ml/forecasting.py`)**: Ridge Regression with time feature engineering (day of week, month, rolling stats).
   - **No-Show Prediction (`ml/no_show_prediction.py`)**: RandomForest Classifier (100 estimators) delivering risk probabilities for upcoming appointments.
   - **Anomaly Detection (`ml/anomaly_detection.py`)**: Isolation Forest identifying statistical outliers in waiting times, volume spikes, and billing irregularities.

5. **Automated Alerts & Copilot Engine (`automation/`, `copilot/`)**:
   - **Alert Engine**: Evaluates capacity thresholds, waiting times, inventory stockouts, and claim denial spikes.
   - **Copilot**: Natural Language operational query parser & daily executive briefing generator.
