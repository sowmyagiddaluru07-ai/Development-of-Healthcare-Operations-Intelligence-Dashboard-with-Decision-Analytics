"""Excel Exporter for Medical Operations Intelligence using pandas / openpyxl."""
import os
import pandas as pd
from datetime import datetime


class ExcelReportExporter:
    """Exports multi-tab Excel workbooks for operations analysis."""

    def __init__(self, db):
        self.db = db

    def export_all_sheets(self, output_path="reports/Medical_Operations_Data_Export.xlsx"):
        """Export all main MongoDB collections into structured Excel sheets."""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        writer = pd.ExcelWriter(output_path, engine='openpyxl')
        
        collections = [
            "patients", "appointments", "admissions", "staff", 
            "billing", "insurance_claims", "pharmacy_inventory",
            "laboratory_tests", "emergency_cases", "quality_incidents"
        ]

        for col in collections:
            docs = list(self.db[col].find({}, {"_id": 0}).limit(1000))
            if docs:
                df = pd.DataFrame(docs)
                # flatten dict columns if any
                df.to_excel(writer, sheet_name=col[:31], index=False)
            else:
                pd.DataFrame({"status": ["No data"]}).to_excel(writer, sheet_name=col[:31], index=False)

        writer.close()
        print(f"✅ Exported Excel workbook: {output_path}")
        return output_path
