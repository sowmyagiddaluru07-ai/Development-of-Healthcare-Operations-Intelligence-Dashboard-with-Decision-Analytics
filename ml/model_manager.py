from ml.forecasting import PatientVolumeForecaster
from ml.no_show_prediction import NoShowPredictor
from ml.revenue_prediction import RevenueForecaster
from ml.anomaly_detection import AnomalyDetector
from ml.staff_forecasting import StaffForecaster
from datetime import datetime

class ModelManager:
    def __init__(self, db):
        self.db = db
        self.patient_forecaster = PatientVolumeForecaster(db)
        self.no_show_predictor = NoShowPredictor(db)
        self.revenue_forecaster = RevenueForecaster(db)
        self.anomaly_detector = AnomalyDetector(db)
        self.staff_forecaster = StaffForecaster(db)
        self.status = {}

    def train_all_models(self, facility_id=None):
        results = {}
        
        try:
            results['patient_forecaster'] = self.patient_forecaster.train(facility_id)
        except Exception as e:
            results['patient_forecaster'] = False
            print(f"Error training patient forecaster: {e}")
            
        try:
            results['no_show_predictor'] = self.no_show_predictor.train(facility_id)
        except Exception as e:
            results['no_show_predictor'] = False
            print(f"Error training no show predictor: {e}")
            
        try:
            results['revenue_forecaster'] = self.revenue_forecaster.train(facility_id)
        except Exception as e:
            results['revenue_forecaster'] = False
            print(f"Error training revenue forecaster: {e}")
            
        self.status = {
            'last_run': datetime.now().isoformat(),
            'results': results
        }
        
        return results

    def get_all_predictions(self, facility_id=None):
        return {
            'volume_forecast': self.patient_forecaster.get_results(),
            'revenue_forecast': self.revenue_forecaster.get_results(),
            'no_show_risks': self.no_show_predictor.get_risk_appointments(facility_id),
            'staffing_needs': self.staff_forecaster.predict_staffing_needs(facility_id),
            'anomalies': self.anomaly_detector.detect_all_anomalies(facility_id)
        }
        
    def get_model_status(self):
        return self.status
