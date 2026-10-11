"""Anomaly detection using Isolation Forest."""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sklearn.ensemble import IsolationForest


class AnomalyDetector:
    def __init__(self, db):
        self.db = db

    def _detect_anomalies(self, values, dates):
        """Run Isolation Forest on a 1D array of values."""
        if len(values) < 10:
            return [{'date': d, 'value': float(v), 'is_anomaly': False, 'anomaly_score': 0.0} for d, v in zip(dates, values)]
        X = np.array(values).reshape(-1, 1)
        clf = IsolationForest(contamination=0.1, random_state=42, n_estimators=100)
        labels = clf.fit_predict(X)
        scores = clf.decision_function(X)
        return [{'date': d, 'value': round(float(v), 2), 'is_anomaly': bool(l == -1),
                 'anomaly_score': round(float(-s), 4)} for d, v, l, s in zip(dates, values, labels, scores)]

    def detect_waiting_time_anomalies(self, facility_id=None):
        """Detect anomalies in daily average waiting times."""
        try:
            match = {'waiting_time_minutes': {'$ne': None}}
            if facility_id:
                match['facility_id'] = facility_id
            pipe = [
                {'$match': match},
                {'$group': {'_id': {'$dateToString': {'format': '%Y-%m-%d', 'date': '$appointment_date'}}, 'avg_wait': {'$avg': '$waiting_time_minutes'}}},
                {'$sort': {'_id': 1}},
            ]
            data = list(self.db['appointments'].aggregate(pipe))
            if not data:
                return []
            dates = [r['_id'] for r in data]
            values = [r['avg_wait'] for r in data]
            return self._detect_anomalies(values, dates)
        except Exception as e:
            print(f'Wait anomaly error: {e}')
            return []

    def detect_volume_anomalies(self, facility_id=None):
        """Detect anomalies in daily appointment counts."""
        try:
            match = {}
            if facility_id:
                match['facility_id'] = facility_id
            pipe = [{'$match': match}] if match else []
            pipe.extend([
                {'$group': {'_id': {'$dateToString': {'format': '%Y-%m-%d', 'date': '$appointment_date'}}, 'count': {'$sum': 1}}},
                {'$sort': {'_id': 1}},
            ])
            data = list(self.db['appointments'].aggregate(pipe))
            if not data:
                return []
            return self._detect_anomalies([r['count'] for r in data], [r['_id'] for r in data])
        except Exception as e:
            print(f'Volume anomaly error: {e}')
            return []

    def detect_revenue_anomalies(self, facility_id=None):
        """Detect anomalies in daily revenue."""
        try:
            match = {}
            if facility_id:
                match['facility_id'] = facility_id
            pipe = [{'$match': match}] if match else []
            pipe.extend([
                {'$group': {'_id': {'$dateToString': {'format': '%Y-%m-%d', 'date': '$bill_date'}}, 'revenue': {'$sum': '$net_amount'}}},
                {'$sort': {'_id': 1}},
            ])
            data = list(self.db['billing'].aggregate(pipe))
            if not data:
                return []
            return self._detect_anomalies([r['revenue'] for r in data], [r['_id'] for r in data])
        except Exception as e:
            print(f'Revenue anomaly error: {e}')
            return []

    def detect_all_anomalies(self, facility_id=None):
        """Run all anomaly detections."""
        return {
            'waiting_time': self.detect_waiting_time_anomalies(facility_id),
            'volume': self.detect_volume_anomalies(facility_id),
            'revenue': self.detect_revenue_anomalies(facility_id),
        }
