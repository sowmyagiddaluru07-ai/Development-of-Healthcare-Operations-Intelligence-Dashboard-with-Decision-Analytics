"""Claims analytics with MongoDB aggregation."""
from datetime import datetime, timedelta
from config.settings import Settings


class ClaimsAnalytics:
    def __init__(self, db):
        self.db = db

    def get_claims_overview(self, facility_id=None):
        """Claims totals and denial rate."""
        try:
            match = {}
            if facility_id:
                match['facility_id'] = facility_id

            status_pipe = [{'$match': match}] if match else []
            status_pipe.append({'$group': {'_id': '$status', 'count': {'$sum': 1}, 'amount': {'$sum': '$claim_amount'}}})
            status_data = list(self.db['insurance_claims'].aggregate(status_pipe))

            total = sum(r['count'] for r in status_data)
            denied = next((r['count'] for r in status_data if r['_id'] == 'Denied'), 0)
            approved = next((r['count'] for r in status_data if r['_id'] == 'Approved'), 0)
            pending = next((r['count'] for r in status_data if r['_id'] == 'Pending'), 0)
            total_amount = sum(r['amount'] for r in status_data)

            avg_pipe = [{'$match': match}] if match else []
            avg_pipe.append({'$group': {'_id': None, 'avg_amount': {'$avg': '$claim_amount'}, 'avg_age': {'$avg': '$claim_age_days'}}})
            avg_result = list(self.db['insurance_claims'].aggregate(avg_pipe))

            return {
                'total_claims': total,
                'approved': approved,
                'denied': denied,
                'pending': pending,
                'denial_rate': round(denied / max(total, 1) * 100, 1),
                'approval_rate': round(approved / max(total, 1) * 100, 1),
                'total_amount': round(total_amount, 2),
                'avg_claim_amount': round(avg_result[0]['avg_amount'], 2) if avg_result else 0,
                'avg_claim_age': round(avg_result[0]['avg_age'], 1) if avg_result and avg_result[0].get('avg_age') else 0,
                'by_status': [{'status': r['_id'], 'count': r['count'], 'amount': round(r['amount'], 2)} for r in status_data],
            }
        except Exception as e:
            print(f'Claims overview error: {e}')
            return {'total_claims': 0, 'approved': 0, 'denied': 0, 'pending': 0, 'denial_rate': 0,
                    'approval_rate': 0, 'total_amount': 0, 'avg_claim_amount': 0, 'avg_claim_age': 0, 'by_status': []}

    def get_denial_analysis(self, facility_id=None):
        """Denial reasons and payer analysis."""
        try:
            match = {'status': 'Denied'}
            if facility_id:
                match['facility_id'] = facility_id

            reason_pipe = [{'$match': match}, {'$group': {'_id': '$denial_reason', 'count': {'$sum': 1}}}, {'$sort': {'count': -1}}]
            by_reason = [{'reason': r['_id'] or 'Unknown', 'count': r['count']} for r in self.db['insurance_claims'].aggregate(reason_pipe)]

            payer_pipe = [{'$match': match}, {'$group': {'_id': '$payer', 'count': {'$sum': 1}}}, {'$sort': {'count': -1}}]
            by_payer = [{'payer': r['_id'], 'count': r['count']} for r in self.db['insurance_claims'].aggregate(payer_pipe)]

            return {'by_reason': by_reason, 'by_payer': by_payer}
        except Exception as e:
            print(f'Denial analysis error: {e}')
            return {'by_reason': [], 'by_payer': []}

    def get_claim_aging(self, facility_id=None):
        """Claim aging distribution."""
        try:
            match = {'status': {'$in': ['Pending', 'Under Review']}}
            if facility_id:
                match['facility_id'] = facility_id
            claims = list(self.db['insurance_claims'].find(match, {'claim_age_days': 1, 'claim_amount': 1}))
            buckets = {'0-15 days': {'count': 0, 'amount': 0}, '16-30 days': {'count': 0, 'amount': 0},
                       '31-60 days': {'count': 0, 'amount': 0}, '60+ days': {'count': 0, 'amount': 0}}
            for c in claims:
                age = c.get('claim_age_days', 0)
                amt = c.get('claim_amount', 0)
                if age <= 15:
                    buckets['0-15 days']['count'] += 1
                    buckets['0-15 days']['amount'] += amt
                elif age <= 30:
                    buckets['16-30 days']['count'] += 1
                    buckets['16-30 days']['amount'] += amt
                elif age <= 60:
                    buckets['31-60 days']['count'] += 1
                    buckets['31-60 days']['amount'] += amt
                else:
                    buckets['60+ days']['count'] += 1
                    buckets['60+ days']['amount'] += amt
            return [{'bucket': k, 'count': v['count'], 'amount': round(v['amount'], 2)} for k, v in buckets.items()]
        except Exception as e:
            print(f'Claim aging error: {e}')
            return []

    def get_payer_comparison(self, facility_id=None):
        """Approval/denial rates by payer."""
        try:
            match = {}
            if facility_id:
                match['facility_id'] = facility_id
            pipe = [{'$match': match}] if match else []
            pipe.extend([
                {'$group': {
                    '_id': {'payer': '$payer', 'status': '$status'},
                    'count': {'$sum': 1},
                    'amount': {'$sum': '$claim_amount'},
                }},
            ])
            raw = list(self.db['insurance_claims'].aggregate(pipe))
            payer_data = {}
            for r in raw:
                payer = r['_id']['payer']
                status = r['_id']['status']
                if payer not in payer_data:
                    payer_data[payer] = {'total': 0, 'approved': 0, 'denied': 0, 'pending': 0}
                payer_data[payer]['total'] += r['count']
                if status == 'Approved':
                    payer_data[payer]['approved'] += r['count']
                elif status == 'Denied':
                    payer_data[payer]['denied'] += r['count']
                else:
                    payer_data[payer]['pending'] += r['count']

            return [{
                'payer': p,
                'total': d['total'],
                'approved': d['approved'],
                'denied': d['denied'],
                'approval_rate': round(d['approved'] / max(d['total'], 1) * 100, 1),
                'denial_rate': round(d['denied'] / max(d['total'], 1) * 100, 1),
            } for p, d in payer_data.items()]
        except Exception as e:
            print(f'Payer comparison error: {e}')
            return []

    def get_claims_trend(self, months=6, facility_id=None):
        """Monthly claims trend."""
        try:
            cutoff = datetime.now() - timedelta(days=months * 30)
            match = {'submission_date': {'$gte': cutoff}}
            if facility_id:
                match['facility_id'] = facility_id
            pipe = [
                {'$match': match},
                {'$group': {
                    '_id': {'month': {'$dateToString': {'format': '%Y-%m', 'date': '$submission_date'}}, 'status': '$status'},
                    'count': {'$sum': 1},
                }},
                {'$sort': {'_id.month': 1}},
            ]
            raw = list(self.db['insurance_claims'].aggregate(pipe))
            month_data = {}
            for r in raw:
                m = r['_id']['month']
                if m not in month_data:
                    month_data[m] = {'month': m, 'total': 0, 'approved': 0, 'denied': 0, 'pending': 0}
                month_data[m]['total'] += r['count']
                s = r['_id']['status']
                if s == 'Approved':
                    month_data[m]['approved'] += r['count']
                elif s == 'Denied':
                    month_data[m]['denied'] += r['count']
                else:
                    month_data[m]['pending'] += r['count']
            return list(month_data.values())
        except Exception as e:
            print(f'Claims trend error: {e}')
            return []
