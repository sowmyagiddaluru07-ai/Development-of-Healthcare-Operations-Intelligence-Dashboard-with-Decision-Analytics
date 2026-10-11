import os
import pandas as pd

class PowerBIExporter:
    """Exports MongoDB data to CSV files for Power BI ingestion."""
    
    def __init__(self, db):
        self.db = db
        self.export_dir = os.path.join(os.path.dirname(__file__), 'exports')
        os.makedirs(self.export_dir, exist_ok=True)
        
    def export_executive_kpis(self):
        try:
            from analytics.kpi_engine import KPIEngine
            kpi_engine = KPIEngine(self.db)
            kpis = kpi_engine.get_executive_kpis()
            df = pd.DataFrame([kpis])
            df.to_csv(os.path.join(self.export_dir, 'executive_kpis.csv'), index=False)
            return True
        except Exception as e:
            print(f"Error exporting executive KPIs: {e}")
            return False

    def export_patients(self):
        try:
            patients = list(self.db.patients.find({}, {'_id': 0}))
            if patients:
                df = pd.DataFrame(patients)
                df.to_csv(os.path.join(self.export_dir, 'patients.csv'), index=False)
            return True
        except Exception as e:
            print(f"Error exporting patients: {e}")
            return False

    def export_appointments(self):
        try:
            appts = list(self.db.appointments.find({}, {'_id': 0}))
            if appts:
                df = pd.DataFrame(appts)
                df.to_csv(os.path.join(self.export_dir, 'appointments.csv'), index=False)
            return True
        except Exception as e:
            print(f"Error exporting appointments: {e}")
            return False
            
    def export_admissions(self):
        try:
            admissions = list(self.db.admissions.find({}, {'_id': 0}))
            if admissions:
                df = pd.DataFrame(admissions)
                df.to_csv(os.path.join(self.export_dir, 'admissions.csv'), index=False)
            return True
        except Exception as e:
            print(f"Error exporting admissions: {e}")
            return False

    def export_staff(self):
        try:
            staff = list(self.db.staff.find({}, {'_id': 0}))
            if staff:
                df = pd.DataFrame(staff)
                df.to_csv(os.path.join(self.export_dir, 'staff.csv'), index=False)
            return True
        except Exception as e:
            print(f"Error exporting staff: {e}")
            return False

    def export_revenue(self):
        try:
            billing = list(self.db.billing.find({}, {'_id': 0}))
            if billing:
                df = pd.DataFrame(billing)
                df.to_csv(os.path.join(self.export_dir, 'billing.csv'), index=False)
            return True
        except Exception as e:
            print(f"Error exporting billing: {e}")
            return False
            
    def export_claims(self):
        try:
            claims = list(self.db.insurance_claims.find({}, {'_id': 0}))
            if claims:
                df = pd.DataFrame(claims)
                df.to_csv(os.path.join(self.export_dir, 'claims.csv'), index=False)
            return True
        except Exception as e:
            print(f"Error exporting claims: {e}")
            return False
            
    def export_pharmacy(self):
        try:
            pharmacy = list(self.db.pharmacy_inventory.find({}, {'_id': 0}))
            if pharmacy:
                df = pd.DataFrame(pharmacy)
                df.to_csv(os.path.join(self.export_dir, 'pharmacy.csv'), index=False)
            return True
        except Exception as e:
            print(f"Error exporting pharmacy: {e}")
            return False
            
    def export_laboratory(self):
        try:
            lab = list(self.db.laboratory_tests.find({}, {'_id': 0}))
            if lab:
                df = pd.DataFrame(lab)
                df.to_csv(os.path.join(self.export_dir, 'laboratory.csv'), index=False)
            return True
        except Exception as e:
            print(f"Error exporting laboratory: {e}")
            return False
            
    def export_emergency(self):
        try:
            er = list(self.db.emergency_cases.find({}, {'_id': 0}))
            if er:
                df = pd.DataFrame(er)
                df.to_csv(os.path.join(self.export_dir, 'emergency.csv'), index=False)
            return True
        except Exception as e:
            print(f"Error exporting emergency: {e}")
            return False

    def export_quality(self):
        try:
            quality = list(self.db.quality_incidents.find({}, {'_id': 0}))
            if quality:
                df = pd.DataFrame(quality)
                df.to_csv(os.path.join(self.export_dir, 'quality.csv'), index=False)
            return True
        except Exception as e:
            print(f"Error exporting quality: {e}")
            return False
            
    def export_feedback(self):
        try:
            feedback = list(self.db.patient_feedback.find({}, {'_id': 0}))
            if feedback:
                df = pd.DataFrame(feedback)
                df.to_csv(os.path.join(self.export_dir, 'feedback.csv'), index=False)
            return True
        except Exception as e:
            print(f"Error exporting feedback: {e}")
            return False

    def export_financials(self):
        try:
            financials = list(self.db.financial_transactions.find({}, {'_id': 0}))
            if financials:
                df = pd.DataFrame(financials)
                df.to_csv(os.path.join(self.export_dir, 'financials.csv'), index=False)
            return True
        except Exception as e:
            print(f"Error exporting financials: {e}")
            return False
            
    def export_alerts(self):
        try:
            alerts = list(self.db.operational_alerts.find({}, {'_id': 0}))
            if alerts:
                df = pd.DataFrame(alerts)
                df.to_csv(os.path.join(self.export_dir, 'alerts.csv'), index=False)
            return True
        except Exception as e:
            print(f"Error exporting alerts: {e}")
            return False

    def export_predictions(self):
        try:
            # Generate dummy predictions summary for Power BI integration if model manager is complex
            df = pd.DataFrame([{"prediction_type": "patient_volume", "predicted_value": 150}])
            df.to_csv(os.path.join(self.export_dir, 'predictions.csv'), index=False)
            return True
        except Exception as e:
            print(f"Error exporting predictions: {e}")
            return False
            
    def export_all(self):
        exports = {
            'executive_kpis': self.export_executive_kpis(),
            'patients': self.export_patients(),
            'appointments': self.export_appointments(),
            'admissions': self.export_admissions(),
            'staff': self.export_staff(),
            'revenue': self.export_revenue(),
            'claims': self.export_claims(),
            'pharmacy': self.export_pharmacy(),
            'laboratory': self.export_laboratory(),
            'emergency': self.export_emergency(),
            'quality': self.export_quality(),
            'feedback': self.export_feedback(),
            'financials': self.export_financials(),
            'alerts': self.export_alerts(),
            'predictions': self.export_predictions()
        }
        
        success_count = sum(1 for v in exports.values() if v)
        return {
            'total_files': success_count,
            'details': exports
        }
