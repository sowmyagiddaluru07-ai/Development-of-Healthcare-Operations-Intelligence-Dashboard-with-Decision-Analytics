def get_dax_documentation():
    return """
# Power BI DAX Measures for Medical Operations Intelligence

## Core Measures

### Financial
Total Revenue = SUM(billing[net_amount])
Total Billed = SUM(billing[total_amount])
Average Revenue per Patient = DIVIDE([Total Revenue], DISTINCTCOUNT(billing[patient_id]))

### Operations
Total Appointments = COUNTROWS(appointments)
Total Admissions = COUNTROWS(admissions)
Average Wait Time (mins) = AVERAGE(appointments[wait_time_minutes])
No-Show Rate = DIVIDE(CALCULATE(COUNTROWS(appointments), appointments[status] == "no_show"), [Total Appointments])

### Facility & Capacity
Bed Utilization Rate = DIVIDE([Total Admissions], [Total Beds Available])

## Recommended Calculated Columns
appointments[Date] = DATE(YEAR(appointments[date_time]), MONTH(appointments[date_time]), DAY(appointments[date_time]))
appointments[Is Late] = IF(appointments[wait_time_minutes] > 15, "Yes", "No")

## Relationship Documentation
- patients (1) -> (*) appointments (on patient_id)
- patients (1) -> (*) admissions (on patient_id)
- patients (1) -> (*) billing (on patient_id)
- staff (1) -> (*) appointments (on staff_id)

## Filter Context Notes
Ensure date dimensions are properly linked for time-intelligence functions like YTD Revenue or MTD Admissions.
"""
