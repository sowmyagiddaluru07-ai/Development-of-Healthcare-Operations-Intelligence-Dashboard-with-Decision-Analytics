"""Revenue analytics with MongoDB aggregation."""
from datetime import datetime, timedelta
from config.settings import Settings


class RevenueAnalytics:
    def __init__(self, db):
        self.db = db

    def get_revenue_summary(self, facility_id=None, start_date=None, end_date=None):
        """Total revenue, by category, by department."""
        try:
            match = {}
            if facility_id:
                match['facility_id'] = facility_id
            if start_date:
                match['bill_date'] = {'$gte': start_date}
            if end_date:
                match.setdefault('bill_date', {})['$lte'] = end_date

            total_pipe = [{'$match': match}] if match else []
            total_pipe.append({'$group': {'_id': None, 'total': {'$sum': '$net_amount'}, 'outstanding': {'$sum': '$outstanding_amount'}, 'count': {'$sum': 1}}})
            tr = list(self.db['billing'].aggregate(total_pipe))
            total = round(tr[0]['total'], 2) if tr else 0
            outstanding = round(tr[0]['outstanding'], 2) if tr else 0
            count = tr[0]['count'] if tr else 0

            cat_pipe = [{'$match': match}] if match else []
            cat_pipe.extend([{'$group': {'_id': '$billing_category', 'revenue': {'$sum': '$net_amount'}}}, {'$sort': {'revenue': -1}}])
            by_category = [{'category': r['_id'], 'revenue': round(r['revenue'], 2)} for r in self.db['billing'].aggregate(cat_pipe)]

            dept_map = {d['id']: d['name'] for d in Settings.DEPARTMENTS}
            dept_pipe = [{'$match': match}] if match else []
            dept_pipe.extend([{'$group': {'_id': '$department_id', 'revenue': {'$sum': '$net_amount'}}}, {'$sort': {'revenue': -1}}])
            by_dept = [{'department': dept_map.get(r['_id'], r['_id']), 'revenue': round(r['revenue'], 2)} for r in self.db['billing'].aggregate(dept_pipe)]

            return {'total_revenue': total, 'outstanding': outstanding, 'bill_count': count,
                    'collection_rate': round((total - outstanding) / max(total, 1) * 100, 1),
                    'by_category': by_category, 'by_department': by_dept}
        except Exception as e:
            print(f'Revenue summary error: {e}')
            return {'total_revenue': 0, 'outstanding': 0, 'bill_count': 0, 'collection_rate': 0, 'by_category': [], 'by_department': []}

    def get_daily_revenue(self, days=30, facility_id=None):
        """Daily revenue trend."""
        try:
            cutoff = datetime.now() - timedelta(days=days)
            match = {'bill_date': {'$gte': cutoff}}
            if facility_id:
                match['facility_id'] = facility_id
            pipe = [
                {'$match': match},
                {'$group': {'_id': {'$dateToString': {'format': '%Y-%m-%d', 'date': '$bill_date'}}, 'revenue': {'$sum': '$net_amount'}, 'count': {'$sum': 1}}},
                {'$sort': {'_id': 1}},
            ]
            return [{'date': r['_id'], 'revenue': round(r['revenue'], 2), 'bills': r['count']} for r in self.db['billing'].aggregate(pipe)]
        except Exception as e:
            print(f'Daily revenue error: {e}')
            return []

    def get_monthly_revenue(self, months=6, facility_id=None):
        """Monthly revenue trend."""
        try:
            cutoff = datetime.now() - timedelta(days=months * 30)
            match = {'bill_date': {'$gte': cutoff}}
            if facility_id:
                match['facility_id'] = facility_id
            pipe = [
                {'$match': match},
                {'$group': {'_id': {'$dateToString': {'format': '%Y-%m', 'date': '$bill_date'}}, 'revenue': {'$sum': '$net_amount'}, 'count': {'$sum': 1}}},
                {'$sort': {'_id': 1}},
            ]
            return [{'month': r['_id'], 'revenue': round(r['revenue'], 2), 'bills': r['count']} for r in self.db['billing'].aggregate(pipe)]
        except Exception as e:
            print(f'Monthly revenue error: {e}')
            return []

    def get_payment_analysis(self, facility_id=None):
        """Payment status distribution."""
        try:
            match = {}
            if facility_id:
                match['facility_id'] = facility_id
            pipe = [{'$match': match}] if match else []
            pipe.extend([{'$group': {'_id': '$payment_status', 'count': {'$sum': 1}, 'amount': {'$sum': '$net_amount'}}}, {'$sort': {'count': -1}}])
            return [{'status': r['_id'], 'count': r['count'], 'amount': round(r['amount'], 2)} for r in self.db['billing'].aggregate(pipe)]
        except Exception as e:
            print(f'Payment analysis error: {e}')
            return []

    def get_outstanding_analysis(self, facility_id=None):
        """Outstanding payment aging buckets."""
        try:
            match = {'payment_status': {'$in': ['Pending', 'Overdue', 'Partial']}}
            if facility_id:
                match['facility_id'] = facility_id
            now = datetime.now()
            bills = list(self.db['billing'].find(match, {'bill_date': 1, 'outstanding_amount': 1}))
            buckets = {'0-30 days': 0, '31-60 days': 0, '61-90 days': 0, '90+ days': 0}
            for b in bills:
                age = (now - b['bill_date']).days if b.get('bill_date') else 0
                amt = b.get('outstanding_amount', 0)
                if age <= 30:
                    buckets['0-30 days'] += amt
                elif age <= 60:
                    buckets['31-60 days'] += amt
                elif age <= 90:
                    buckets['61-90 days'] += amt
                else:
                    buckets['90+ days'] += amt
            return [{'bucket': k, 'amount': round(v, 2)} for k, v in buckets.items()]
        except Exception as e:
            print(f'Outstanding analysis error: {e}')
            return []

    def get_revenue_by_doctor(self, facility_id=None):
        """Revenue per doctor (top 15)."""
        try:
            match = {}
            if facility_id:
                match['facility_id'] = facility_id
            pipe = [{'$match': match}] if match else []
            pipe.extend([
                {'$group': {'_id': '$doctor_id', 'revenue': {'$sum': '$net_amount'}, 'bills': {'$sum': 1}}},
                {'$sort': {'revenue': -1}},
                {'$limit': 15},
            ])
            staff_map = {}
            for s in self.db['staff'].find({'role': 'Doctor'}, {'staff_id': 1, 'first_name': 1, 'last_name': 1}):
                staff_map[s['staff_id']] = f"Dr. {s.get('first_name', '')} {s.get('last_name', '')}"
            return [{
                'doctor': staff_map.get(r['_id'], r['_id']),
                'revenue': round(r['revenue'], 2),
                'bills': r['bills'],
            } for r in self.db['billing'].aggregate(pipe)]
        except Exception as e:
            print(f'Revenue by doctor error: {e}')
            return []

    def get_cost_vs_revenue(self, facility_id=None):
        """Revenue vs expense from financial transactions."""
        try:
            match = {}
            if facility_id:
                match['facility_id'] = facility_id
            pipe = [{'$match': match}] if match else []
            pipe.extend([{'$group': {'_id': '$type', 'total': {'$sum': '$amount'}, 'budget': {'$sum': '$budget_amount'}}}])
            data = list(self.db['financial_transactions'].aggregate(pipe))
            result = {}
            for r in data:
                result[r['_id']] = {'actual': round(r['total'], 2), 'budget': round(r['budget'], 2)}
            return result
        except Exception as e:
            print(f'Cost vs revenue error: {e}')
            return {}
