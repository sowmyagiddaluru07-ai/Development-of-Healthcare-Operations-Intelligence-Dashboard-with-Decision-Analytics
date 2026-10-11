import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sklearn.linear_model import Ridge
from bson.objectid import ObjectId

class StaffForecaster:
    def __init__(self, db):
        self.db = db
        self.model = Ridge(alpha=1.0)
        
    def predict_staffing_needs(self, facility_id=None, days=14):
        try:
            match_stage = {}
            if facility_id:
                match_stage['facility_id'] = ObjectId(facility_id) if isinstance(facility_id, str) else facility_id

            pipeline = [
                {"$match": match_stage} if match_stage else {"$match": {}},
                {"$group": {
                    "_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$scheduled_time"}},
                    "count": {"$sum": 1}
                }},
                {"$sort": {"_id": 1}}
            ]
            
            cursor = self.db.appointments.aggregate(pipeline)
            data = list(cursor)
            
            if not data or len(data) < 10:
                return []

            df = pd.DataFrame(data)
            df['date'] = pd.to_datetime(df['_id'])
            df['day_of_week'] = df['date'].dt.dayofweek
            df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
            
            X = df[['day_of_week', 'is_weekend']]
            y = df['count']
            
            self.model.fit(X, y)
            
            last_date = df['date'].max()
            future_dates = [last_date + timedelta(days=i) for i in range(1, days + 1)]
            
            future_df = pd.DataFrame({'date': future_dates})
            future_df['day_of_week'] = future_df['date'].dt.dayofweek
            future_df['is_weekend'] = future_df['day_of_week'].isin([5, 6]).astype(int)
            
            X_future = future_df[['day_of_week', 'is_weekend']]
            predictions = self.model.predict(X_future)
            
            results = []
            for i, date in enumerate(future_dates):
                expected_volume = max(0, int(predictions[i]))
                # Assuming 1 staff member per 15 appointments
                needed_staff = max(1, int(np.ceil(expected_volume / 15.0)))
                
                results.append({
                    'date': date.strftime('%Y-%m-%d'),
                    'expected_volume': expected_volume,
                    'recommended_staff': needed_staff
                })
                
            return results
        except Exception as e:
            print(f"Error predicting staffing needs: {e}")
            return []
            
    def get_coverage_gaps(self, facility_id=None):
        try:
            predictions = self.predict_staffing_needs(facility_id, days=14)
            if not predictions:
                return []
                
            query = {'status': 'Active'}
            if facility_id:
                query['facility_id'] = ObjectId(facility_id) if isinstance(facility_id, str) else facility_id
                
            current_staff = self.db.staff.count_documents(query)
            
            gaps = []
            for p in predictions:
                gap = p['recommended_staff'] - current_staff
                if gap > 0:
                    gaps.append({
                        'date': p['date'],
                        'current_staff': current_staff,
                        'recommended_staff': p['recommended_staff'],
                        'gap': gap
                    })
            return gaps
        except Exception as e:
            print(f"Error getting coverage gaps: {e}")
            return []
