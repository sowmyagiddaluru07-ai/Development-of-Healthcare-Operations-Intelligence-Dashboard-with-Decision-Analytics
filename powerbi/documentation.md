# Power BI Integration Documentation

## Overview
This document covers how to integrate the exported CSV data from the Medical Operations Intelligence system into Power BI.

## How to import CSVs into Power BI
1. Run the `export_engine.py` script to generate the CSV exports in the `powerbi/exports/` directory.
2. In Power BI Desktop, go to **Home > Get Data > Text/CSV**.
3. Select each CSV file and click **Load**. Alternatively, use **Transform Data** to apply any initial formatting (like parsing dates).

## Recommended Relationships
- `patients[patient_id]` -> `appointments[patient_id]` (1 to Many)
- `patients[patient_id]` -> `admissions[patient_id]` (1 to Many)
- `patients[patient_id]` -> `billing[patient_id]` (1 to Many)
- `staff[staff_id]` -> `appointments[staff_id]` (1 to Many)
- `staff[staff_id]` -> `admissions[attending_doctor_id]` (1 to Many)

## Suggested Dashboard Pages
1. **Executive Summary**: High-level KPIs (Revenue, Volume, Health Score).
2. **Patient Flow**: Admissions, Discharges, Wait Times.
3. **Revenue & Billing**: Total revenue, claims status, payment collection.
4. **Staff Performance**: Appointments per doctor, utilization.
5. **Quality & Safety**: Incidents, feedback scores.
6. **Pharmacy & Inventory**: Stock levels, usage rates.
7. **Emergency Department**: Triage times, case types.
8. **Predictive Insights**: No-show predictions, volume forecasts.
9. **Facility Management**: Bed utilization, department loads.
10. **Operational Alerts**: Unresolved alerts, system notifications.

## Key DAX Measures
See `dax_measures.py` for a full list of DAX formulas.
Examples include `Total Revenue`, `No-Show Rate`, and `Average Wait Time`.

## Recommended Visuals
- **Executive Summary**: Card visuals for KPIs, Line chart for Revenue over time.
- **Patient Flow**: Sankey diagram or Funnel chart.
- **Quality**: Gauge or Donut charts for patient satisfaction scores.
- **Emergency**: Map visual (if geographic data present) or scatter plots for wait time vs severity.

## Field Mappings
- Dates should be formatted as `Date/Time` in Power BI for proper hierarchy generation.
- Currency fields (`total_amount`, `net_amount`) should be formatted as decimal numbers and categorized as Currency.
