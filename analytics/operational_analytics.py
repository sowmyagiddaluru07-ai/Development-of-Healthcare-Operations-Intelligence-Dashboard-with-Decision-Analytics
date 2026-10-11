"""Operational analytics for pharmacy, lab, emergency, quality, vendors, finance."""
from datetime import datetime, timedelta
from config.settings import Settings


class OperationalAnalytics:
    def __init__(self, db):
        self.db = db

    def get_pharmacy_status(self, facility_id=None):
        """Pharmacy inventory status."""
        try:
            match = {}
            if facility_id:
                match['facility_id'] = facility_id

            total = self.db['pharmacy_inventory'].count_documents(match)

            low_stock = list(self.db['pharmacy_inventory'].find(
                {**match, '$expr': {'$lt': ['$stock_quantity', '$reorder_level']}},
                {'medicine_id': 1, 'name': 1, 'stock_quantity': 1, 'reorder_level': 1, 'facility_id': 1, 'category': 1}
            ).sort('stock_quantity', 1).limit(50))
            low_items = [{'id': r['medicine_id'], 'name': r.get('name', ''), 'stock': r['stock_quantity'],
                          'reorder': r['reorder_level'], 'category': r.get('category', '')} for r in low_stock]

            expiry_cutoff = datetime.now() + timedelta(days=30)
            near_expiry = list(self.db['pharmacy_inventory'].find(
                {**match, 'expiry_date': {'$lte': expiry_cutoff}},
                {'medicine_id': 1, 'name': 1, 'expiry_date': 1, 'stock_quantity': 1, 'facility_id': 1}
            ).sort('expiry_date', 1).limit(50))
            expiry_items = [{'id': r['medicine_id'], 'name': r.get('name', ''),
                             'expiry': r['expiry_date'].strftime('%Y-%m-%d') if r.get('expiry_date') else '',
                             'stock': r.get('stock_quantity', 0)} for r in near_expiry]

            cat_pipe = [{'$match': match}] if match else []
            cat_pipe.extend([{'$group': {'_id': '$category', 'count': {'$sum': 1}, 'total_stock': {'$sum': '$stock_quantity'}}}, {'$sort': {'count': -1}}])
            by_cat = [{'category': r['_id'], 'count': r['count'], 'total_stock': r['total_stock']} for r in self.db['pharmacy_inventory'].aggregate(cat_pipe)]

            return {'total_items': total, 'low_stock_count': len(low_items), 'near_expiry_count': len(expiry_items),
                    'low_stock_items': low_items, 'near_expiry_items': expiry_items, 'by_category': by_cat}
        except Exception as e:
            print(f'Pharmacy error: {e}')
            return {'total_items': 0, 'low_stock_count': 0, 'near_expiry_count': 0, 'low_stock_items': [], 'near_expiry_items': [], 'by_category': []}

    def get_lab_analytics(self, facility_id=None):
        """Laboratory test analytics."""
        try:
            match = {}
            if facility_id:
                match['facility_id'] = facility_id

            total = self.db['laboratory_tests'].count_documents(match)
            pending = self.db['laboratory_tests'].count_documents({**match, 'status': 'Pending'})

            avg_pipe = [{'$match': match}] if match else []
            avg_pipe.append({'$group': {'_id': None, 'avg_tat': {'$avg': '$turnaround_hours'}}})
            avg_r = list(self.db['laboratory_tests'].aggregate(avg_pipe))
            avg_tat = round(avg_r[0]['avg_tat'], 1) if avg_r and avg_r[0].get('avg_tat') else 0

            by_test_pipe = [{'$match': match}] if match else []
            by_test_pipe.extend([{'$group': {'_id': '$test_name', 'count': {'$sum': 1}, 'avg_tat': {'$avg': '$turnaround_hours'}}}, {'$sort': {'count': -1}}])
            by_test = [{'test': r['_id'], 'count': r['count'], 'avg_tat': round(r.get('avg_tat') or 0, 1)} for r in self.db['laboratory_tests'].aggregate(by_test_pipe)]

            status_pipe = [{'$match': match}] if match else []
            status_pipe.append({'$group': {'_id': '$status', 'count': {'$sum': 1}}})
            by_status = [{'status': r['_id'], 'count': r['count']} for r in self.db['laboratory_tests'].aggregate(status_pipe)]

            return {'total_tests': total, 'pending': pending, 'avg_turnaround': avg_tat, 'by_test': by_test, 'by_status': by_status}
        except Exception as e:
            print(f'Lab analytics error: {e}')
            return {'total_tests': 0, 'pending': 0, 'avg_turnaround': 0, 'by_test': [], 'by_status': []}

    def get_emergency_analytics(self, facility_id=None):
        """Emergency department analytics."""
        try:
            match = {}
            if facility_id:
                match['facility_id'] = facility_id

            total = self.db['emergency_cases'].count_documents(match)
            avg_pipe = [{'$match': match}] if match else []
            avg_pipe.append({'$group': {'_id': None, 'avg_wait': {'$avg': '$waiting_time_minutes'}, 'avg_treat': {'$avg': '$treatment_duration_minutes'}}})
            avg_r = list(self.db['emergency_cases'].aggregate(avg_pipe))
            avg_wait = round(avg_r[0]['avg_wait'], 1) if avg_r and avg_r[0].get('avg_wait') else 0
            avg_treat = round(avg_r[0]['avg_treat'], 1) if avg_r and avg_r[0].get('avg_treat') else 0

            triage_pipe = [{'$match': match}] if match else []
            triage_pipe.extend([{'$group': {'_id': '$triage_level', 'count': {'$sum': 1}, 'avg_wait': {'$avg': '$waiting_time_minutes'}}}, {'$sort': {'_id': 1}}])
            by_triage = [{'level': f"Level {r['_id']}", 'count': r['count'], 'avg_wait': round(r.get('avg_wait') or 0, 1)} for r in self.db['emergency_cases'].aggregate(triage_pipe)]

            disp_pipe = [{'$match': match}] if match else []
            disp_pipe.append({'$group': {'_id': '$disposition', 'count': {'$sum': 1}}})
            by_disp = [{'disposition': r['_id'], 'count': r['count']} for r in self.db['emergency_cases'].aggregate(disp_pipe)]

            complaint_pipe = [{'$match': match}] if match else []
            complaint_pipe.extend([{'$group': {'_id': '$chief_complaint', 'count': {'$sum': 1}}}, {'$sort': {'count': -1}}, {'$limit': 10}])
            by_complaint = [{'complaint': r['_id'], 'count': r['count']} for r in self.db['emergency_cases'].aggregate(complaint_pipe)]

            return {'total_cases': total, 'avg_wait': avg_wait, 'avg_treatment': avg_treat,
                    'by_triage': by_triage, 'by_disposition': by_disp, 'by_complaint': by_complaint}
        except Exception as e:
            print(f'Emergency analytics error: {e}')
            return {'total_cases': 0, 'avg_wait': 0, 'avg_treatment': 0, 'by_triage': [], 'by_disposition': [], 'by_complaint': []}

    def get_quality_metrics(self, facility_id=None):
        """Quality incident metrics."""
        try:
            match = {}
            if facility_id:
                match['facility_id'] = facility_id

            total = self.db['quality_incidents'].count_documents(match)
            resolved = self.db['quality_incidents'].count_documents({**match, 'status': {'$in': ['Resolved', 'Closed']}})
            resolution_rate = round(resolved / max(total, 1) * 100, 1)

            type_pipe = [{'$match': match}] if match else []
            type_pipe.extend([{'$group': {'_id': '$incident_type', 'count': {'$sum': 1}}}, {'$sort': {'count': -1}}])
            by_type = [{'type': r['_id'], 'count': r['count']} for r in self.db['quality_incidents'].aggregate(type_pipe)]

            sev_pipe = [{'$match': match}] if match else []
            sev_pipe.append({'$group': {'_id': '$severity', 'count': {'$sum': 1}}})
            by_severity = [{'severity': r['_id'], 'count': r['count']} for r in self.db['quality_incidents'].aggregate(sev_pipe)]

            avg_pipe = [{'$match': {**match, 'days_to_resolve': {'$ne': None}}}]
            avg_pipe.append({'$group': {'_id': None, 'avg': {'$avg': '$days_to_resolve'}}})
            avg_r = list(self.db['quality_incidents'].aggregate(avg_pipe))
            avg_resolve = round(avg_r[0]['avg'], 1) if avg_r and avg_r[0].get('avg') else 0

            return {'total': total, 'resolved': resolved, 'resolution_rate': resolution_rate,
                    'avg_resolution_days': avg_resolve, 'by_type': by_type, 'by_severity': by_severity}
        except Exception as e:
            print(f'Quality metrics error: {e}')
            return {'total': 0, 'resolved': 0, 'resolution_rate': 0, 'avg_resolution_days': 0, 'by_type': [], 'by_severity': []}

    def get_feedback_analytics(self, facility_id=None):
        """Patient feedback and satisfaction."""
        try:
            match = {}
            if facility_id:
                match['facility_id'] = facility_id

            avg_pipe = [{'$match': match}] if match else []
            avg_pipe.append({'$group': {'_id': None, 'avg_rating': {'$avg': '$rating'}, 'avg_nps': {'$avg': '$nps_score'}, 'count': {'$sum': 1}}})
            avg_r = list(self.db['patient_feedback'].aggregate(avg_pipe))
            avg_rating = round(avg_r[0]['avg_rating'], 2) if avg_r and avg_r[0].get('avg_rating') else 0
            avg_nps = round(avg_r[0]['avg_nps'], 1) if avg_r and avg_r[0].get('avg_nps') else 0
            total = avg_r[0]['count'] if avg_r else 0

            sent_pipe = [{'$match': match}] if match else []
            sent_pipe.append({'$group': {'_id': '$sentiment', 'count': {'$sum': 1}}})
            by_sentiment = [{'sentiment': r['_id'], 'count': r['count']} for r in self.db['patient_feedback'].aggregate(sent_pipe)]

            cat_pipe = [{'$match': match}] if match else []
            cat_pipe.extend([{'$group': {'_id': '$category', 'count': {'$sum': 1}, 'avg_rating': {'$avg': '$rating'}}}, {'$sort': {'count': -1}}])
            by_category = [{'category': r['_id'], 'count': r['count'], 'avg_rating': round(r['avg_rating'], 2)} for r in self.db['patient_feedback'].aggregate(cat_pipe)]

            complaints = self.db['patient_feedback'].count_documents({**match, 'complaint_status': {'$ne': None}})
            resolved_complaints = self.db['patient_feedback'].count_documents({**match, 'complaint_status': 'Resolved'})

            # CSAT (% rating 4 or 5)
            promoters = self.db['patient_feedback'].count_documents({**match, 'rating': {'$gte': 4}})
            csat = round(promoters / max(total, 1) * 100, 1)

            return {'avg_rating': avg_rating, 'avg_nps': avg_nps, 'csat': csat, 'total_feedback': total,
                    'complaints': complaints, 'resolved_complaints': resolved_complaints,
                    'by_sentiment': by_sentiment, 'by_category': by_category}
        except Exception as e:
            print(f'Feedback analytics error: {e}')
            return {'avg_rating': 0, 'avg_nps': 0, 'csat': 0, 'total_feedback': 0,
                    'complaints': 0, 'resolved_complaints': 0, 'by_sentiment': [], 'by_category': []}

    def get_vendor_analytics(self):
        """Vendor performance metrics."""
        try:
            total = self.db['vendors'].count_documents({})
            active = self.db['vendors'].count_documents({'status': 'Active'})

            cat_pipe = [{'$group': {'_id': '$category', 'count': {'$sum': 1}, 'avg_rating': {'$avg': '$rating'}, 'avg_reliability': {'$avg': '$delivery_reliability'}}}, {'$sort': {'count': -1}}]
            by_cat = [{'category': r['_id'], 'count': r['count'],
                       'avg_rating': round(r.get('avg_rating') or 0, 1),
                       'avg_reliability': round((r.get('avg_reliability') or 0) * 100, 1)} for r in self.db['vendors'].aggregate(cat_pipe)]

            avg_pipe = [{'$group': {'_id': None, 'avg_rating': {'$avg': '$rating'}, 'avg_reliability': {'$avg': '$delivery_reliability'}}}]
            avg_r = list(self.db['vendors'].aggregate(avg_pipe))

            return {'total': total, 'active': active,
                    'avg_rating': round(avg_r[0]['avg_rating'], 1) if avg_r else 0,
                    'avg_reliability': round((avg_r[0]['avg_reliability'] or 0) * 100, 1) if avg_r else 0,
                    'by_category': by_cat}
        except Exception as e:
            print(f'Vendor analytics error: {e}')
            return {'total': 0, 'active': 0, 'avg_rating': 0, 'avg_reliability': 0, 'by_category': []}

    def get_financial_overview(self, facility_id=None):
        """Financial summary - revenue vs expenses."""
        try:
            match = {}
            if facility_id:
                match['facility_id'] = facility_id

            type_pipe = [{'$match': match}] if match else []
            type_pipe.append({'$group': {'_id': '$type', 'total': {'$sum': '$amount'}, 'budget': {'$sum': '$budget_amount'}}})
            by_type = {r['_id']: {'actual': round(r['total'], 2), 'budget': round(r['budget'], 2)} for r in self.db['financial_transactions'].aggregate(type_pipe)}

            cat_pipe = [{'$match': match}] if match else []
            cat_pipe.extend([{'$group': {'_id': {'type': '$type', 'category': '$category'}, 'total': {'$sum': '$amount'}}}, {'$sort': {'total': -1}}])
            by_cat = [{'type': r['_id']['type'], 'category': r['_id']['category'], 'amount': round(r['total'], 2)} for r in self.db['financial_transactions'].aggregate(cat_pipe)]

            revenue = by_type.get('Revenue', {}).get('actual', 0)
            expense = by_type.get('Expense', {}).get('actual', 0)

            return {'revenue': revenue, 'expense': expense, 'profit': round(revenue - expense, 2),
                    'profit_margin': round((revenue - expense) / max(revenue, 1) * 100, 1),
                    'by_type': by_type, 'by_category': by_cat}
        except Exception as e:
            print(f'Financial overview error: {e}')
            return {'revenue': 0, 'expense': 0, 'profit': 0, 'profit_margin': 0, 'by_type': {}, 'by_category': []}

    def get_supply_chain_analytics(self, facility_id=None):
        """Purchase order and supply chain analytics."""
        try:
            match = {}
            if facility_id:
                match['facility_id'] = facility_id

            total = self.db['purchase_orders'].count_documents(match)
            status_pipe = [{'$match': match}] if match else []
            status_pipe.append({'$group': {'_id': '$status', 'count': {'$sum': 1}, 'amount': {'$sum': '$total_amount'}}})
            by_status = [{'status': r['_id'], 'count': r['count'], 'amount': round(r['amount'], 2)} for r in self.db['purchase_orders'].aggregate(status_pipe)]

            delay_pipe = [{'$match': {**match, 'delivery_delay_days': {'$gt': 0}}}]
            delay_pipe.append({'$group': {'_id': None, 'avg_delay': {'$avg': '$delivery_delay_days'}, 'count': {'$sum': 1}}})
            delay_r = list(self.db['purchase_orders'].aggregate(delay_pipe))
            avg_delay = round(delay_r[0]['avg_delay'], 1) if delay_r and delay_r[0].get('avg_delay') else 0
            delayed_count = delay_r[0]['count'] if delay_r else 0

            return {'total_orders': total, 'by_status': by_status, 'avg_delay_days': avg_delay, 'delayed_count': delayed_count}
        except Exception as e:
            print(f'Supply chain error: {e}')
            return {'total_orders': 0, 'by_status': [], 'avg_delay_days': 0, 'delayed_count': 0}
