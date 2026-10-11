import unittest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestConfiguration(unittest.TestCase):
    def test_settings_load(self):
        from config.settings import Settings
        self.assertIsNotNone(Settings.APP_NAME)
        self.assertEqual(Settings.DATABASE_NAME, 'medical_operations')
    
    def test_facilities_exist(self):
        from config.settings import Settings
        self.assertEqual(len(Settings.FACILITIES), 4)
    
    def test_departments_exist(self):
        from config.settings import Settings
        self.assertEqual(len(Settings.DEPARTMENTS), 10)
    
    def test_collections_defined(self):
        from config.settings import Settings
        self.assertEqual(len(Settings.COLLECTIONS), 17)

class TestDataGenerators(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from data.generators import SyntheticDataGenerator
        cls.gen = SyntheticDataGenerator()
    
    def test_generate_patients(self):
        patients = self.gen.generate_patients(100)
        self.assertEqual(len(patients), 100)
        self.assertIn('patient_id', patients[0])
        self.assertIn('first_name', patients[0])
        self.assertIn('facility_id', patients[0])
    
    def test_generate_staff(self):
        staff = self.gen.generate_staff(20)
        self.assertEqual(len(staff), 20)
        self.assertIn('staff_id', staff[0])
        self.assertIn('role', staff[0])
    
    def test_generate_appointments(self):
        patients = self.gen.generate_patients(50)
        staff = self.gen.generate_staff(10)
        appts = self.gen.generate_appointments(100, patients, staff)
        self.assertEqual(len(appts), 100)
        # Verify references
        patient_ids = {p['patient_id'] for p in patients}
        for appt in appts:
            self.assertIn(appt['patient_id'], patient_ids)
    
    def test_generate_admissions(self):
        patients = self.gen.generate_patients(50)
        staff = self.gen.generate_staff(10)
        adm = self.gen.generate_admissions(100, patients, staff)
        self.assertEqual(len(adm), 100)
    
    def test_generate_billing(self):
        patients = self.gen.generate_patients(50)
        staff = self.gen.generate_staff(10)
        bills = self.gen.generate_billing(100, patients, staff)
        self.assertEqual(len(bills), 100)
        self.assertTrue(all(b['net_amount'] >= 0 for b in bills))
    
    def test_generate_insurance_claims(self):
        patients = self.gen.generate_patients(50)
        claims = self.gen.generate_insurance_claims(100, patients)
        self.assertEqual(len(claims), 100)
    
    def test_generate_pharmacy(self):
        items = self.gen.generate_pharmacy_inventory(50)
        self.assertEqual(len(items), 50)
        self.assertIn('medicine_id', items[0])
    
    def test_generate_lab_tests(self):
        patients = self.gen.generate_patients(50)
        staff = self.gen.generate_staff(10)
        tests = self.gen.generate_laboratory_tests(100, patients, staff)
        self.assertEqual(len(tests), 100)
    
    def test_generate_emergency(self):
        patients = self.gen.generate_patients(50)
        staff = self.gen.generate_staff(10)
        cases = self.gen.generate_emergency_cases(100, patients, staff)
        self.assertEqual(len(cases), 100)
    
    def test_generate_quality(self):
        incidents = self.gen.generate_quality_incidents(50)
        self.assertEqual(len(incidents), 50)
    
    def test_generate_feedback(self):
        patients = self.gen.generate_patients(50)
        feedback = self.gen.generate_patient_feedback(100, patients)
        self.assertEqual(len(feedback), 100)
    
    def test_generate_vendors(self):
        vendors = self.gen.generate_vendors(10)
        self.assertEqual(len(vendors), 10)
    
    def test_generate_purchase_orders(self):
        pos = self.gen.generate_purchase_orders(50)
        self.assertEqual(len(pos), 50)
    
    def test_generate_financial(self):
        txns = self.gen.generate_financial_transactions(100)
        self.assertEqual(len(txns), 100)

class TestAnalytics(unittest.TestCase):
    def test_kpi_engine_import(self):
        from analytics.kpi_engine import KPIEngine
        self.assertIsNotNone(KPIEngine)
    
    def test_patient_analytics_import(self):
        from analytics.patient_analytics import PatientAnalytics
        self.assertIsNotNone(PatientAnalytics)
    
    def test_staff_analytics_import(self):
        from analytics.staff_analytics import StaffAnalytics
        self.assertIsNotNone(StaffAnalytics)
    
    def test_revenue_analytics_import(self):
        from analytics.revenue_analytics import RevenueAnalytics
        self.assertIsNotNone(RevenueAnalytics)
    
    def test_claims_analytics_import(self):
        from analytics.claims_analytics import ClaimsAnalytics
        self.assertIsNotNone(ClaimsAnalytics)
    
    def test_operational_analytics_import(self):
        from analytics.operational_analytics import OperationalAnalytics
        self.assertIsNotNone(OperationalAnalytics)

class TestMLModels(unittest.TestCase):
    def test_forecasting_import(self):
        from ml.forecasting import PatientVolumeForecaster
        self.assertIsNotNone(PatientVolumeForecaster)
    
    def test_no_show_import(self):
        from ml.no_show_prediction import NoShowPredictor
        self.assertIsNotNone(NoShowPredictor)
    
    def test_revenue_prediction_import(self):
        from ml.revenue_prediction import RevenueForecaster
        self.assertIsNotNone(RevenueForecaster)
    
    def test_anomaly_detection_import(self):
        from ml.anomaly_detection import AnomalyDetector
        self.assertIsNotNone(AnomalyDetector)
    
    def test_model_manager_import(self):
        from ml.model_manager import ModelManager
        self.assertIsNotNone(ModelManager)

class TestAutomation(unittest.TestCase):
    def test_alert_engine_import(self):
        from automation.alert_engine import AlertEngine
        self.assertIsNotNone(AlertEngine)
    
    def test_audit_logger_import(self):
        from automation.audit_logger import AuditLogger
        self.assertIsNotNone(AuditLogger)

class TestCopilot(unittest.TestCase):
    def test_copilot_import(self):
        from copilot.query_engine import OperationsCopilot
        self.assertIsNotNone(OperationsCopilot)
    
    def test_insights_import(self):
        from copilot.insights_engine import InsightsEngine
        self.assertIsNotNone(InsightsEngine)

class TestPowerBI(unittest.TestCase):
    def test_exporter_import(self):
        from powerbi.export_engine import PowerBIExporter
        self.assertIsNotNone(PowerBIExporter)

if __name__ == '__main__':
    unittest.main(verbosity=2)
