"""No-show prediction using Random Forest."""
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
from sklearn.preprocessing import LabelEncoder


class NoShowPredictor:
    def __init__(self, db):
        self.db = db
        self.model = None
        self.metrics = {}
        self.feature_names = []
        self.label_encoders = {}
        self.is_trained = False

    def prepare_features(self, facility_id=None):
        """Build features from appointment data."""
        try:
            match = {'status': {'$in': ['Completed', 'No-show']}}
            if facility_id:
                match['facility_id'] = facility_id
            data = list(self.db['appointments'].find(match, {
                'appointment_type': 1, 'department_id': 1, 'appointment_date': 1,
                'waiting_time_minutes': 1, 'status': 1, 'patient_id': 1,
            }))
            if len(data) < 100:
                return None, None
            df = pd.DataFrame(data)
            df['is_no_show'] = (df['status'] == 'No-show').astype(int)
            df['day_of_week'] = pd.to_datetime(df['appointment_date']).dt.dayofweek
            df['hour'] = pd.to_datetime(df['appointment_date']).dt.hour
            df['waiting_time_minutes'] = df['waiting_time_minutes'].fillna(0)

            for col in ['appointment_type', 'department_id']:
                le = LabelEncoder()
                df[col + '_enc'] = le.fit_transform(df[col].astype(str))
                self.label_encoders[col] = le

            self.feature_names = ['appointment_type_enc', 'department_id_enc', 'day_of_week', 'hour', 'waiting_time_minutes']
            X = df[self.feature_names].values
            y = df['is_no_show'].values
            return X, y
        except Exception as e:
            print(f'Feature prep error: {e}')
            return None, None

    def train(self, facility_id=None):
        """Train RandomForest classifier."""
        try:
            X, y = self.prepare_features(facility_id)
            if X is None:
                self.metrics = {'error': 'Insufficient data'}
                return False
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
            self.model = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
            self.model.fit(X_train, y_train)
            y_pred = self.model.predict(X_test)
            y_proba = self.model.predict_proba(X_test)[:, 1]
            self.metrics = {
                'accuracy': round(accuracy_score(y_test, y_pred), 4),
                'precision': round(precision_score(y_test, y_pred, zero_division=0), 4),
                'recall': round(recall_score(y_test, y_pred, zero_division=0), 4),
                'f1': round(f1_score(y_test, y_pred, zero_division=0), 4),
                'auc': round(roc_auc_score(y_test, y_proba), 4),
                'train_size': len(X_train),
                'test_size': len(X_test),
            }
            self.is_trained = True
            return True
        except Exception as e:
            self.metrics = {'error': str(e)}
            return False

    def get_feature_importance(self):
        """Get feature importance rankings."""
        if not self.is_trained:
            return []
        importances = self.model.feature_importances_
        return sorted([{'feature': n, 'importance': round(float(v), 4)} for n, v in zip(self.feature_names, importances)], key=lambda x: x['importance'], reverse=True)

    def get_risk_appointments(self, facility_id=None):
        """Find scheduled appointments with highest no-show risk."""
        if not self.is_trained:
            return []
        try:
            match = {'status': 'Scheduled'}
            if facility_id:
                match['facility_id'] = facility_id
            data = list(self.db['appointments'].find(match).limit(200))
            if not data:
                return []
            df = pd.DataFrame(data)
            df['day_of_week'] = pd.to_datetime(df['appointment_date']).dt.dayofweek
            df['hour'] = pd.to_datetime(df['appointment_date']).dt.hour
            df['waiting_time_minutes'] = df['waiting_time_minutes'].fillna(0)
            for col in ['appointment_type', 'department_id']:
                le = self.label_encoders.get(col)
                if le:
                    df[col + '_enc'] = df[col].astype(str).apply(lambda x: le.transform([x])[0] if x in le.classes_ else 0)
                else:
                    df[col + '_enc'] = 0
            X = df[self.feature_names].values
            probs = self.model.predict_proba(X)[:, 1]
            df['no_show_probability'] = probs
            top = df.nlargest(20, 'no_show_probability')
            return [{'appointment_id': r.get('appointment_id', ''), 'patient_id': r.get('patient_id', ''),
                     'date': str(r.get('appointment_date', '')), 'type': r.get('appointment_type', ''),
                     'probability': round(float(r['no_show_probability']), 3)} for _, r in top.iterrows()]
        except Exception as e:
            print(f'Risk appointments error: {e}')
            return []
