"""Revenue forecasting using Ridge regression."""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sklearn.linear_model import Ridge
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


class RevenueForecaster:
    def __init__(self, db):
        self.db = db
        self.model = None
        self.metrics = {}
        self.historical_data = None
        self.predictions = None
        self.is_trained = False

    def prepare_data(self, facility_id=None):
        try:
            match = {}
            if facility_id:
                match['facility_id'] = facility_id
            pipe = []
            if match:
                pipe.append({'$match': match})
            pipe.extend([
                {'$group': {'_id': {'$dateToString': {'format': '%Y-%m', 'date': '$bill_date'}}, 'revenue': {'$sum': '$net_amount'}}},
                {'$sort': {'_id': 1}},
            ])
            results = list(self.db['billing'].aggregate(pipe))
            if not results:
                return None
            df = pd.DataFrame(results)
            df.columns = ['month', 'revenue']
            df['date'] = pd.to_datetime(df['month'] + '-01')
            df['month_num'] = range(len(df))
            df['month_of_year'] = df['date'].dt.month
            self.historical_data = df
            return df
        except Exception as e:
            print(f'Revenue data prep error: {e}')
            return None

    def train(self, facility_id=None):
        try:
            df = self.prepare_data(facility_id)
            if df is None or len(df) < 3:
                self.metrics = {'error': 'Insufficient data'}
                return False
            X = df[['month_num', 'month_of_year']].values
            y = df['revenue'].values
            if len(df) > 4:
                X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)
            else:
                X_train, y_train = X, y
                X_test, y_test = X, y
            self.model = Ridge(alpha=1.0)
            self.model.fit(X_train, y_train)
            y_pred = self.model.predict(X_test)
            self.metrics = {
                'mae': round(float(mean_absolute_error(y_test, y_pred)), 2),
                'rmse': round(float(np.sqrt(mean_squared_error(y_test, y_pred))), 2),
                'r2': round(float(r2_score(y_test, y_pred)), 4) if len(y_test) > 1 else 0,
            }
            self.is_trained = True
            return True
        except Exception as e:
            self.metrics = {'error': str(e)}
            return False

    def predict(self, months=3):
        if not self.is_trained:
            return []
        try:
            last_num = self.historical_data['month_num'].max()
            last_date = self.historical_data['date'].max()
            preds = []
            for i in range(1, months + 1):
                future_date = last_date + pd.DateOffset(months=i)
                X_new = np.array([[last_num + i, future_date.month]])
                pred = float(self.model.predict(X_new)[0])
                preds.append({'month': future_date.strftime('%Y-%m'), 'predicted_revenue': round(max(0, pred), 2)})
            self.predictions = preds
            return preds
        except Exception as e:
            print(f'Revenue predict error: {e}')
            return []

    def get_results(self):
        hist = []
        if self.historical_data is not None:
            hist = [{'month': r['month'], 'revenue': round(float(r['revenue']), 2)} for _, r in self.historical_data.iterrows()]
        return {'historical': hist, 'predictions': self.predictions or [], 'metrics': self.metrics, 'is_trained': self.is_trained}
