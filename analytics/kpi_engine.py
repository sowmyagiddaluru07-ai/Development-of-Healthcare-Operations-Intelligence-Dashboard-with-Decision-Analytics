"""Central KPI computation engine using MongoDB aggregation."""
from datetime import datetime, timedelta
from config.settings import Settings


class KPIEngine:
    def __init__(self, db):
        self.db = db

    def get_executive_kpis(self, facility_id=None, department_id=None, start_date=None, end_date=None):
        """Compute all executive KPIs from MongoDB."""
        try:
            f = {}
            if facility_id:
                f['facility_id'] = facility_id
            if department_id:
                f['department_id'] = department_id

            pf = {'facility_id': facility_id} if facility_id else {}
            total_patients = self.db['patients'].count_documents(pf)

            total_appts = self.db['appointments'].count_documents(f)
            no_shows = self.db['appointments'].count_documents({**f, 'status': 'No-show'})
            cancelled = self.db['appointments'].count_documents({**f, 'status': 'Cancelled'})
            no_show_rate = round(no_shows / max(total_appts, 1) * 100, 1)
            cancel_rate = round(cancelled / max(total_appts, 1) * 100, 1)

            wait_pipe = []
            if f:
                wait_pipe.append({'$match': f})
            wait_pipe.append({'$match': {'waiting_time_minutes': {'$ne': None}}})
            wait_pipe.append({'$group': {'_id': None, 'avg': {'$avg': '$waiting_time_minutes'}}})
            wr = list(self.db['appointments'].aggregate(wait_pipe))
            avg_wait = round(wr[0]['avg'], 1) if wr and wr[0].get('avg') else 0

            total_adm = self.db['admissions'].count_documents(f)
            total_dis = self.db['admissions'].count_documents({**f, 'status': 'Discharged'})

            los_pipe = []
            if f:
                los_pipe.append({'$match': f})
            los_pipe.append({'$match': {'length_of_stay_days': {'$exists': True, '$ne': None}}})
            los_pipe.append({'$group': {'_id': None, 'avg': {'$avg': '$length_of_stay_days'}}})
            lr = list(self.db['admissions'].aggregate(los_pipe))
            avg_los = round(lr[0]['avg'], 1) if lr and lr[0].get('avg') else 0

            admitted = self.db['admissions'].count_documents({**f, 'status': 'Admitted'})
            total_beds = sum(fac['beds'] for fac in Settings.FACILITIES)
            if facility_id:
                total_beds = next((fac['beds'] for fac in Settings.FACILITIES if fac['id'] == facility_id), total_beds)
            bed_util = round(admitted / max(total_beds, 1) * 100, 1)

            sf = {'status': 'Active'}
            if facility_id:
                sf['facility_id'] = facility_id
            su_pipe = [{'$match': sf}, {'$group': {'_id': None, 'avg': {'$avg': '$utilization_rate'}}}]
            sr = list(self.db['staff'].aggregate(su_pipe))
            staff_util = round(sr[0]['avg'] * 100, 1) if sr and sr[0].get('avg') else 0

            rev_pipe = []
            if f:
                rev_pipe.append({'$match': f})
            rev_pipe.append({'$group': {'_id': None, 'total': {'$sum': '$net_amount'}, 'outstanding': {'$sum': '$outstanding_amount'}}})
            rr = list(self.db['billing'].aggregate(rev_pipe))
            total_rev = round(rr[0]['total'], 2) if rr and rr[0].get('total') else 0
            outstanding = round(rr[0]['outstanding'], 2) if rr and rr[0].get('outstanding') else 0

            cf = {'facility_id': facility_id} if facility_id else {}
            total_claims = self.db['insurance_claims'].count_documents(cf)
            denied = self.db['insurance_claims'].count_documents({**cf, 'status': 'Denied'})
            denial_rate = round(denied / max(total_claims, 1) * 100, 1)

            sat_pipe = []
            if f:
                sat_pipe.append({'$match': f})
            sat_pipe.append({'$group': {'_id': None, 'avg': {'$avg': '$rating'}}})
            satr = list(self.db['patient_feedback'].aggregate(sat_pipe))
            avg_sat = round(satr[0]['avg'], 2) if satr and satr[0].get('avg') else 0

            hs = self._compute_health_score(avg_wait, bed_util, staff_util, no_show_rate, denial_rate, avg_sat, total_rev, outstanding)

            return {
                'total_patients': total_patients,
                'total_appointments': total_appts,
                'total_admissions': total_adm,
                'total_discharges': total_dis,
                'no_show_rate': no_show_rate,
                'cancellation_rate': cancel_rate,
                'avg_waiting_time': avg_wait,
                'avg_length_of_stay': avg_los,
                'bed_utilization': bed_util,
                'staff_utilization': staff_util,
                'total_revenue': total_rev,
                'outstanding_payments': outstanding,
                'claim_denial_rate': denial_rate,
                'avg_patient_satisfaction': avg_sat,
                'operational_health_score': hs['score'],
                'health_score_breakdown': hs['breakdown'],
            }
        except Exception as e:
            print(f'KPI Error: {e}')
            return {k: 0 for k in ['total_patients', 'total_appointments', 'total_admissions',
                                    'total_discharges', 'no_show_rate', 'cancellation_rate',
                                    'avg_waiting_time', 'avg_length_of_stay', 'bed_utilization',
                                    'staff_utilization', 'total_revenue', 'outstanding_payments',
                                    'claim_denial_rate', 'avg_patient_satisfaction', 'operational_health_score',
                                    'health_score_breakdown']}

    def _compute_health_score(self, wait_time, bed_util, staff_util, no_show, denial, satisfaction, revenue, outstanding):
        """Compute operational health score 0-100 with weighted components."""
        try:
            wait_score = max(0, (1 - wait_time / 60)) * 100
            bed_score = max(0, (1 - abs(bed_util - 80) / 80)) * 100
            staff_score = max(0, (1 - abs(staff_util - 75) / 75)) * 100
            noshow_score = max(0, (1 - no_show / 30)) * 100
            denial_score = max(0, (1 - denial / 30)) * 100
            sat_score = (satisfaction / 5) * 100 if satisfaction else 50
            rev_score = max(0, (1 - outstanding / (revenue + 1))) * 100 if revenue > 0 else 50

            weights = {
                'waiting_time': 0.15,
                'bed_utilization': 0.15,
                'staff_utilization': 0.15,
                'no_show_rate': 0.10,
                'claim_denial': 0.10,
                'satisfaction': 0.20,
                'revenue': 0.15,
            }
            scores = {
                'waiting_time': round(wait_score, 1),
                'bed_utilization': round(bed_score, 1),
                'staff_utilization': round(staff_score, 1),
                'no_show_rate': round(noshow_score, 1),
                'claim_denial': round(denial_score, 1),
                'satisfaction': round(sat_score, 1),
                'revenue': round(rev_score, 1),
            }
            total = sum(scores[k] * weights[k] for k in weights)
            return {'score': round(min(100, max(0, total)), 1), 'breakdown': scores}
        except Exception:
            return {'score': 0, 'breakdown': {}}

    def get_operational_health_score(self, facility_id=None):
        """Get operational health score with breakdown."""
        kpis = self.get_executive_kpis(facility_id=facility_id)
        return {
            'score': kpis.get('operational_health_score', 0),
            'breakdown': kpis.get('health_score_breakdown', {}),
        }

    def get_daily_trends(self, days=30, facility_id=None):
        """Get daily appointment and revenue trends."""
        try:
            cutoff = datetime.now() - timedelta(days=days)
            match = {'appointment_date': {'$gte': cutoff}}
            if facility_id:
                match['facility_id'] = facility_id

            pipe = [
                {'$match': match},
                {'$group': {
                    '_id': {'$dateToString': {'format': '%Y-%m-%d', 'date': '$appointment_date'}},
                    'appointments': {'$sum': 1},
                    'avg_wait': {'$avg': '$waiting_time_minutes'},
                }},
                {'$sort': {'_id': 1}},
            ]
            appt_data = list(self.db['appointments'].aggregate(pipe))

            rev_match = {'bill_date': {'$gte': cutoff}}
            if facility_id:
                rev_match['facility_id'] = facility_id
            rev_pipe = [
                {'$match': rev_match},
                {'$group': {
                    '_id': {'$dateToString': {'format': '%Y-%m-%d', 'date': '$bill_date'}},
                    'revenue': {'$sum': '$net_amount'},
                }},
                {'$sort': {'_id': 1}},
            ]
            rev_data = list(self.db['billing'].aggregate(rev_pipe))
            rev_map = {r['_id']: r['revenue'] for r in rev_data}

            results = []
            for d in appt_data:
                results.append({
                    'date': d['_id'],
                    'appointments': d['appointments'],
                    'avg_wait': round(d.get('avg_wait') or 0, 1),
                    'revenue': round(rev_map.get(d['_id'], 0), 2),
                })
            return results
        except Exception as e:
            print(f'Daily trends error: {e}')
            return []

    def get_monthly_trends(self, months=6, facility_id=None):
        """Get monthly aggregated KPIs."""
        try:
            cutoff = datetime.now() - timedelta(days=months * 30)
            match = {'appointment_date': {'$gte': cutoff}}
            if facility_id:
                match['facility_id'] = facility_id

            pipe = [
                {'$match': match},
                {'$group': {
                    '_id': {'$dateToString': {'format': '%Y-%m', 'date': '$appointment_date'}},
                    'appointments': {'$sum': 1},
                    'no_shows': {'$sum': {'$cond': [{'$eq': ['$status', 'No-show']}, 1, 0]}},
                    'avg_wait': {'$avg': '$waiting_time_minutes'},
                }},
                {'$sort': {'_id': 1}},
            ]
            data = list(self.db['appointments'].aggregate(pipe))

            rev_match = {'bill_date': {'$gte': cutoff}}
            if facility_id:
                rev_match['facility_id'] = facility_id
            rev_pipe = [
                {'$match': rev_match},
                {'$group': {
                    '_id': {'$dateToString': {'format': '%Y-%m', 'date': '$bill_date'}},
                    'revenue': {'$sum': '$net_amount'},
                }},
                {'$sort': {'_id': 1}},
            ]
            rev_data = list(self.db['billing'].aggregate(rev_pipe))
            rev_map = {r['_id']: r['revenue'] for r in rev_data}

            results = []
            for d in data:
                total = d['appointments']
                results.append({
                    'month': d['_id'],
                    'appointments': total,
                    'no_show_rate': round(d['no_shows'] / max(total, 1) * 100, 1),
                    'avg_wait': round(d.get('avg_wait') or 0, 1),
                    'revenue': round(rev_map.get(d['_id'], 0), 2),
                })
            return results
        except Exception as e:
            print(f'Monthly trends error: {e}')
            return []

    def get_department_comparison(self, facility_id=None):
        """Get KPIs by department."""
        try:
            match = {}
            if facility_id:
                match['facility_id'] = facility_id

            pipe = [{'$match': match}] if match else []
            pipe.extend([
                {'$group': {
                    '_id': '$department_id',
                    'appointments': {'$sum': 1},
                    'no_shows': {'$sum': {'$cond': [{'$eq': ['$status', 'No-show']}, 1, 0]}},
                    'avg_wait': {'$avg': '$waiting_time_minutes'},
                }},
                {'$sort': {'appointments': -1}},
            ])
            data = list(self.db['appointments'].aggregate(pipe))

            dept_map = {d['id']: d['name'] for d in Settings.DEPARTMENTS}
            results = []
            for d in data:
                dept_name = dept_map.get(d['_id'], d['_id'] or 'Unknown')
                total = d['appointments']
                results.append({
                    'department': dept_name,
                    'department_id': d['_id'],
                    'appointments': total,
                    'no_show_rate': round(d['no_shows'] / max(total, 1) * 100, 1),
                    'avg_wait': round(d.get('avg_wait') or 0, 1),
                })
            return results
        except Exception as e:
            print(f'Department comparison error: {e}')
            return []

    def get_facility_comparison(self):
        """Get KPIs by facility."""
        try:
            pipe = [
                {'$group': {
                    '_id': '$facility_id',
                    'appointments': {'$sum': 1},
                    'no_shows': {'$sum': {'$cond': [{'$eq': ['$status', 'No-show']}, 1, 0]}},
                    'avg_wait': {'$avg': '$waiting_time_minutes'},
                }},
                {'$sort': {'appointments': -1}},
            ]
            data = list(self.db['appointments'].aggregate(pipe))

            fac_map = {f['id']: f['name'] for f in Settings.FACILITIES}
            rev_pipe = [
                {'$group': {
                    '_id': '$facility_id',
                    'revenue': {'$sum': '$net_amount'},
                }},
            ]
            rev_data = list(self.db['billing'].aggregate(rev_pipe))
            rev_map = {r['_id']: r['revenue'] for r in rev_data}

            results = []
            for d in data:
                fac_name = fac_map.get(d['_id'], d['_id'] or 'Unknown')
                total = d['appointments']
                results.append({
                    'facility': fac_name,
                    'facility_id': d['_id'],
                    'appointments': total,
                    'no_show_rate': round(d['no_shows'] / max(total, 1) * 100, 1),
                    'avg_wait': round(d.get('avg_wait') or 0, 1),
                    'revenue': round(rev_map.get(d['_id'], 0), 2),
                })
            return results
        except Exception as e:
            print(f'Facility comparison error: {e}')
            return []
