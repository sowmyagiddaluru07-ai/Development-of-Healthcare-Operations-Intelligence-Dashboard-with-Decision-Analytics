"""Staff analytics with MongoDB aggregation."""
from datetime import datetime, timedelta
from config.settings import Settings


class StaffAnalytics:
    def __init__(self, db):
        self.db = db

    def get_staff_overview(self, facility_id=None):
        """Staff counts by role, department, facility."""
        try:
            match = {}
            if facility_id:
                match['facility_id'] = facility_id

            role_pipe = [{'$match': match}] if match else []
            role_pipe.append({'$group': {'_id': '$role', 'count': {'$sum': 1}}})
            by_role = [{'role': r['_id'], 'count': r['count']} for r in self.db['staff'].aggregate(role_pipe)]

            dept_map = {d['id']: d['name'] for d in Settings.DEPARTMENTS}
            dept_pipe = [{'$match': match}] if match else []
            dept_pipe.extend([{'$group': {'_id': '$department_id', 'count': {'$sum': 1}}}, {'$sort': {'count': -1}}])
            by_dept = [{'department': dept_map.get(r['_id'], r['_id']), 'count': r['count']} for r in self.db['staff'].aggregate(dept_pipe)]

            fac_map = {f['id']: f['name'] for f in Settings.FACILITIES}
            fac_pipe = [{'$match': match}] if match else []
            fac_pipe.append({'$group': {'_id': '$facility_id', 'count': {'$sum': 1}}})
            by_fac = [{'facility': fac_map.get(r['_id'], r['_id']), 'count': r['count']} for r in self.db['staff'].aggregate(fac_pipe)]

            total = self.db['staff'].count_documents(match)
            active = self.db['staff'].count_documents({**match, 'status': 'Active'})
            return {'total': total, 'active': active, 'by_role': by_role, 'by_department': by_dept, 'by_facility': by_fac}
        except Exception as e:
            print(f'Staff overview error: {e}')
            return {'total': 0, 'active': 0, 'by_role': [], 'by_department': [], 'by_facility': []}

    def get_doctor_productivity(self, facility_id=None):
        """Appointments and revenue per doctor."""
        try:
            match = {}
            if facility_id:
                match['facility_id'] = facility_id

            appt_pipe = [{'$match': match}] if match else []
            appt_pipe.extend([
                {'$group': {'_id': '$doctor_id', 'appointments': {'$sum': 1}, 'avg_wait': {'$avg': '$waiting_time_minutes'}}},
                {'$sort': {'appointments': -1}},
                {'$limit': 20},
            ])
            appt_data = {r['_id']: r for r in self.db['appointments'].aggregate(appt_pipe)}

            rev_pipe = [{'$match': match}] if match else []
            rev_pipe.extend([{'$group': {'_id': '$doctor_id', 'revenue': {'$sum': '$net_amount'}}}])
            rev_data = {r['_id']: r['revenue'] for r in self.db['billing'].aggregate(rev_pipe)}

            staff_map = {}
            for s in self.db['staff'].find({'role': 'Doctor'}, {'staff_id': 1, 'first_name': 1, 'last_name': 1, 'department_id': 1}):
                staff_map[s['staff_id']] = f"Dr. {s.get('first_name', '')} {s.get('last_name', '')}"

            dept_map = {d['id']: d['name'] for d in Settings.DEPARTMENTS}
            results = []
            for doc_id, data in appt_data.items():
                results.append({
                    'doctor_id': doc_id,
                    'name': staff_map.get(doc_id, doc_id),
                    'appointments': data['appointments'],
                    'avg_wait': round(data.get('avg_wait') or 0, 1),
                    'revenue': round(rev_data.get(doc_id, 0), 2),
                })
            return results
        except Exception as e:
            print(f'Doctor productivity error: {e}')
            return []

    def get_staff_utilization(self, facility_id=None):
        """Staff utilization rates."""
        try:
            match = {'status': 'Active'}
            if facility_id:
                match['facility_id'] = facility_id

            dept_map = {d['id']: d['name'] for d in Settings.DEPARTMENTS}
            pipe = [
                {'$match': match},
                {'$group': {
                    '_id': '$department_id',
                    'avg_utilization': {'$avg': '$utilization_rate'},
                    'avg_overtime': {'$avg': '$overtime_hours'},
                    'count': {'$sum': 1},
                }},
                {'$sort': {'avg_utilization': -1}},
            ]
            data = list(self.db['staff'].aggregate(pipe))
            return [{
                'department': dept_map.get(r['_id'], r['_id']),
                'avg_utilization': round((r['avg_utilization'] or 0) * 100, 1),
                'avg_overtime': round(r.get('avg_overtime') or 0, 1),
                'staff_count': r['count'],
            } for r in data]
        except Exception as e:
            print(f'Staff utilization error: {e}')
            return []

    def get_workload_analysis(self, facility_id=None):
        """Workload distribution by department."""
        try:
            match = {}
            if facility_id:
                match['facility_id'] = facility_id
            dept_map = {d['id']: d['name'] for d in Settings.DEPARTMENTS}
            pipe = [{'$match': match}] if match else []
            pipe.extend([
                {'$group': {'_id': '$department_id', 'appointments': {'$sum': 1}}},
                {'$sort': {'appointments': -1}},
            ])
            data = list(self.db['appointments'].aggregate(pipe))
            return [{'department': dept_map.get(r['_id'], r['_id']), 'appointments': r['appointments']} for r in data]
        except Exception as e:
            print(f'Workload error: {e}')
            return []

    def get_shift_coverage(self, facility_id=None):
        """Staff count by shift."""
        try:
            match = {'status': 'Active'}
            if facility_id:
                match['facility_id'] = facility_id
            pipe = [{'$match': match}, {'$group': {'_id': '$shift', 'count': {'$sum': 1}}}, {'$sort': {'_id': 1}}]
            return [{'shift': r['_id'], 'count': r['count']} for r in self.db['staff'].aggregate(pipe)]
        except Exception as e:
            print(f'Shift coverage error: {e}')
            return []

    def get_overtime_alerts(self, threshold=10):
        """Staff with excessive overtime."""
        try:
            data = list(self.db['staff'].find(
                {'overtime_hours': {'$gt': threshold}, 'status': 'Active'},
                {'staff_id': 1, 'first_name': 1, 'last_name': 1, 'role': 1, 'department_id': 1, 'overtime_hours': 1, 'facility_id': 1}
            ).sort('overtime_hours', -1))
            dept_map = {d['id']: d['name'] for d in Settings.DEPARTMENTS}
            return [{
                'staff_id': s['staff_id'],
                'name': f"{s.get('first_name', '')} {s.get('last_name', '')}",
                'role': s.get('role', ''),
                'department': dept_map.get(s.get('department_id'), ''),
                'overtime_hours': s['overtime_hours'],
            } for s in data]
        except Exception as e:
            print(f'Overtime alerts error: {e}')
            return []
