"""Patient volume forecasting using Ridge regression."""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sklearn.linear_model import Ridge
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


class PatientVolumeForecaster:
    def __init__(self, db):
        self.db = db
        self.model = None
        self.metrics = {}
        self.historical_data = None
        self.predictions = None
        self.is_trained = False

    def prepare_data(self, facility_id=None):
        """Get daily appointment counts from MongoDB."""
        try:
            match = {}
            if facility_id:
                match['facility_id'] = facility_id
            pipeline = []
            if match:
                pipeline.append({'$match': match})
            pipeline.extend([
                {'$group': {'_id': {'$dateToString': {'format': '%Y-%m-%d', 'date': '$appointment_date'}}, 'count': {'$sum': 1}}},
                {'$sort': {'_id': 1}},
            ])
            results = list(self.db['appointments'].aggregate(pipeline))
            if not results:
                return None
            df = pd.DataFrame(results)
            df.columns = ['date', 'count']
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date').reset_index(drop=True)
            df['day_of_week'] = df['date'].dt.dayofweek
            df['day_of_month'] = df['date'].dt.day
            df['month'] = df['date'].dt.month
            df['is_weekend'] = (df['day_of_week'] >= 5).astype(int)
            df['week_of_year'] = df['date'].dt.isocalendar().week.astype(int)
            df['day_number'] = (df['date'] - df['date'].min()).dt.days
            self.historical_data = df
            return df
        except Exception as e:
            print(f'Forecast data prep error: {e}')
            return None

    def train(self, facility_id=None):
        """Train Ridge regression model."""
        try:
            df = self.prepare_data(facility_id)
            if df is None or len(df) < 14:
                self.metrics = {'error': 'Insufficient data (need 14+ days)'}
                return False
            features = ['day_of_week', 'day_of_month', 'month', 'is_weekend', 'week_of_year', 'day_number']
            X = df[features].values
            y = df['count'].values
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)
            self.model = Ridge(alpha=1.0)
            self.model.fit(X_train, y_train)
            y_pred = self.model.predict(X_test)
            self.metrics = {
                'mae': round(mean_absolute_error(y_test, y_pred), 2),
                'rmse': round(np.sqrt(mean_squared_error(y_test, y_pred)), 2),
                'r2': round(r2_score(y_test, y_pred), 4),
                'train_size': len(X_train),
                'test_size': len(X_test),
            }
            self.is_trained = True
            return True
        except Exception as e:
            self.metrics = {'error': str(e)}
            return False

    def predict(self, days=30):
        """Predict next N days."""
        if not self.is_trained or self.model is None:
            return []
        try:
            last_date = self.historical_data['date'].max()
            last_day_num = self.historical_data['day_number'].max()
            future_dates = [last_date + timedelta(days=i + 1) for i in range(days)]
            future_df = pd.DataFrame({'date': future_dates})
            future_df['day_of_week'] = future_df['date'].dt.dayofweek
            future_df['day_of_month'] = future_df['date'].dt.day
            future_df['month'] = future_df['date'].dt.month
            future_df['is_weekend'] = (future_df['day_of_week'] >= 5).astype(int)
            future_df['week_of_year'] = future_df['date'].dt.isocalendar().week.astype(int)
            future_df['day_number'] = [last_day_num + i + 1 for i in range(days)]
            features = ['day_of_week', 'day_of_month', 'month', 'is_weekend', 'week_of_year', 'day_number']
            preds = self.model.predict(future_df[features].values)
            rmse = self.metrics.get('rmse', 10)
            self.predictions = [{'date': d.strftime('%Y-%m-%d'), 'predicted_count': max(0, round(float(p))),
                                  'lower_bound': max(0, round(float(p - 1.96 * rmse))),
                                  'upper_bound': round(float(p + 1.96 * rmse))} for d, p in zip(future_dates, preds)]
            return self.predictions
        except Exception as e:
            print(f'Forecast predict error: {e}')
            return []

    def get_results(self):
        """Return all results."""
        hist = []
        if self.historical_data is not None:
            hist = [{'date': r['date'].strftime('%Y-%m-%d'), 'count': int(r['count'])} for _, r in self.historical_data.iterrows()]
        return {'historical': hist, 'predictions': self.predictions or [], 'metrics': self.metrics, 'is_trained': self.is_trained}
