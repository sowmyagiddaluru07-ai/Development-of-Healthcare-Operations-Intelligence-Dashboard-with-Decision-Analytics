"""Patient analytics with MongoDB aggregation."""
from datetime import datetime, timedelta
from config.settings import Settings


class PatientAnalytics:
    def __init__(self, db):
        self.db = db

    def get_patient_flow(self, facility_id=None, days=30):
        """Daily patient registrations, admissions, discharges."""
        try:
            cutoff = datetime.now() - timedelta(days=days if days is not None else 30)
            match = {'registration_date': {'$gte': cutoff}}
            if facility_id:
                match['facility_id'] = facility_id

            reg_pipe = [
                {'$match': match},
                {'$group': {'_id': {'$dateToString': {'format': '%Y-%m-%d', 'date': '$registration_date'}}, 'count': {'$sum': 1}}},
                {'$sort': {'_id': 1}},
            ]
            regs = {r['_id']: r['count'] for r in self.db['patients'].aggregate(reg_pipe)}

            adm_match = {'admission_date': {'$gte': cutoff}}
            if facility_id:
                adm_match['facility_id'] = facility_id
            adm_pipe = [
                {'$match': adm_match},
                {'$group': {'_id': {'$dateToString': {'format': '%Y-%m-%d', 'date': '$admission_date'}}, 'count': {'$sum': 1}}},
                {'$sort': {'_id': 1}},
            ]
            adms = {r['_id']: r['count'] for r in self.db['admissions'].aggregate(adm_pipe)}

            dis_match = {'discharge_date': {'$gte': cutoff, '$ne': None}}
            if facility_id:
                dis_match['facility_id'] = facility_id
            dis_pipe = [
                {'$match': dis_match},
                {'$group': {'_id': {'$dateToString': {'format': '%Y-%m-%d', 'date': '$discharge_date'}}, 'count': {'$sum': 1}}},
                {'$sort': {'_id': 1}},
            ]
            diss = {r['_id']: r['count'] for r in self.db['admissions'].aggregate(dis_pipe)}

            all_dates = sorted(set(list(regs.keys()) + list(adms.keys()) + list(diss.keys())))
            return [{'date': d, 'registrations': regs.get(d, 0), 'admissions': adms.get(d, 0), 'discharges': diss.get(d, 0)} for d in all_dates]
        except Exception as e:
            print(f'Patient flow error: {e}')
            return []

    def get_appointment_analytics(self, facility_id=None, dept_id=None):
        """Appointment status and type distributions."""
        try:
            match = {}
            if facility_id:
                match['facility_id'] = facility_id
            if dept_id:
                match['department_id'] = dept_id

            status_pipe = [{'$match': match}] if match else []
            status_pipe.append({'$group': {'_id': '$status', 'count': {'$sum': 1}}})
            status_data = [{'status': r['_id'], 'count': r['count']} for r in self.db['appointments'].aggregate(status_pipe)]

            type_pipe = [{'$match': match}] if match else []
            type_pipe.append({'$group': {'_id': '$appointment_type', 'count': {'$sum': 1}}})
            type_data = [{'type': r['_id'], 'count': r['count']} for r in self.db['appointments'].aggregate(type_pipe)]

            dept_map = {d['id']: d['name'] for d in Settings.DEPARTMENTS}
            dept_pipe = [{'$match': match}] if match else []
            dept_pipe.extend([
                {'$group': {'_id': '$department_id', 'count': {'$sum': 1}}},
                {'$sort': {'count': -1}},
            ])
            dept_data = [{'department': dept_map.get(r['_id'], r['_id']), 'count': r['count']} for r in self.db['appointments'].aggregate(dept_pipe)]

            return {'status_distribution': status_data, 'type_distribution': type_data, 'by_department': dept_data}
        except Exception as e:
            print(f'Appointment analytics error: {e}')
            return {'status_distribution': [], 'type_distribution': [], 'by_department': []}

    def get_waiting_time_analysis(self, facility_id=None):
        """Waiting time statistics by department."""
        try:
            match = {'waiting_time_minutes': {'$ne': None}}
            if facility_id:
                match['facility_id'] = facility_id

            dept_map = {d['id']: d['name'] for d in Settings.DEPARTMENTS}
            pipe = [
                {'$match': match},
                {'$group': {
                    '_id': '$department_id',
                    'avg_wait': {'$avg': '$waiting_time_minutes'},
                    'min_wait': {'$min': '$waiting_time_minutes'},
                    'max_wait': {'$max': '$waiting_time_minutes'},
                    'count': {'$sum': 1},
                }},
                {'$sort': {'avg_wait': -1}},
            ]
            data = list(self.db['appointments'].aggregate(pipe))
            return [{
                'department': dept_map.get(r['_id'], r['_id']),
                'avg_wait': round(r['avg_wait'], 1),
                'min_wait': r['min_wait'],
                'max_wait': r['max_wait'],
                'count': r['count'],
            } for r in data]
        except Exception as e:
            print(f'Waiting time error: {e}')
            return []

    def get_admission_analytics(self, facility_id=None):
        """Admission LOS distribution, readmission rate."""
        try:
            match = {}
            if facility_id:
                match['facility_id'] = facility_id

            # LOS distribution
            los_pipe = [{'$match': {**match, 'length_of_stay_days': {'$ne': None}}}]
            los_pipe.extend([
                {'$bucket': {
                    'groupBy': '$length_of_stay_days',
                    'boundaries': [0, 2, 5, 8, 15, 31],
                    'default': '30+',
                    'output': {'count': {'$sum': 1}},
                }},
            ])
            try:
                los_data = [{'range': f"{r['_id']}", 'count': r['count']} for r in self.db['admissions'].aggregate(los_pipe)]
            except Exception:
                los_data = []

            total = self.db['admissions'].count_documents(match) or 1
            readmissions = self.db['admissions'].count_documents({**match, 'is_readmission': True})
            readmission_rate = round(readmissions / total * 100, 1)

            admitted = self.db['admissions'].count_documents({**match, 'status': 'Admitted'})

            return {
                'los_distribution': los_data,
                'readmission_rate': readmission_rate,
                'total_admissions': total,
                'currently_admitted': admitted,
            }
        except Exception as e:
            print(f'Admission analytics error: {e}')
            return {'los_distribution': [], 'readmission_rate': 0, 'total_admissions': 0, 'currently_admitted': 0}

    def get_patient_demographics(self, facility_id=None):
        """Patient demographics distributions."""
        try:
            match = {}
            if facility_id:
                match['facility_id'] = facility_id

            age_pipe = [{'$match': match}] if match else []
            age_pipe.extend([{'$group': {'_id': '$demographics.age_group', 'count': {'$sum': 1}}}, {'$sort': {'_id': 1}}])
            age_data = [{'age_group': r['_id'], 'count': r['count']} for r in self.db['patients'].aggregate(age_pipe)]

            gender_pipe = [{'$match': match}] if match else []
            gender_pipe.append({'$group': {'_id': '$gender', 'count': {'$sum': 1}}})
            gender_data = [{'gender': r['_id'], 'count': r['count']} for r in self.db['patients'].aggregate(gender_pipe)]

            ins_pipe = [{'$match': match}] if match else []
            ins_pipe.append({'$group': {'_id': '$demographics.insurance_status', 'count': {'$sum': 1}}})
            ins_data = [{'insurance_status': r['_id'], 'count': r['count']} for r in self.db['patients'].aggregate(ins_pipe)]

            return {'age_groups': age_data, 'gender': gender_data, 'insurance': ins_data}
        except Exception as e:
            print(f'Demographics error: {e}')
            return {'age_groups': [], 'gender': [], 'insurance': []}

    def get_no_show_analysis(self, facility_id=None):
        """No-show rates by department, type, day of week."""
        try:
            match = {}
            if facility_id:
                match['facility_id'] = facility_id

            dept_map = {d['id']: d['name'] for d in Settings.DEPARTMENTS}

            dept_pipe = [{'$match': match}] if match else []
            dept_pipe.extend([
                {'$group': {
                    '_id': '$department_id',
                    'total': {'$sum': 1},
                    'no_shows': {'$sum': {'$cond': [{'$eq': ['$status', 'No-show']}, 1, 0]}},
                }},
                {'$sort': {'no_shows': -1}},
            ])
            dept_data = [{
                'department': dept_map.get(r['_id'], r['_id']),
                'total': r['total'],
                'no_shows': r['no_shows'],
                'rate': round(r['no_shows'] / max(r['total'], 1) * 100, 1),
            } for r in self.db['appointments'].aggregate(dept_pipe)]

            type_pipe = [{'$match': match}] if match else []
            type_pipe.extend([
                {'$group': {
                    '_id': '$appointment_type',
                    'total': {'$sum': 1},
                    'no_shows': {'$sum': {'$cond': [{'$eq': ['$status', 'No-show']}, 1, 0]}},
                }},
            ])
            type_data = [{
                'type': r['_id'],
                'total': r['total'],
                'no_shows': r['no_shows'],
                'rate': round(r['no_shows'] / max(r['total'], 1) * 100, 1),
            } for r in self.db['appointments'].aggregate(type_pipe)]

            dow_pipe = [{'$match': match}] if match else []
            dow_pipe.extend([
                {'$group': {
                    '_id': {'$dayOfWeek': '$appointment_date'},
                    'total': {'$sum': 1},
                    'no_shows': {'$sum': {'$cond': [{'$eq': ['$status', 'No-show']}, 1, 0]}},
                }},
                {'$sort': {'_id': 1}},
            ])
            day_names = {1: 'Sun', 2: 'Mon', 3: 'Tue', 4: 'Wed', 5: 'Thu', 6: 'Fri', 7: 'Sat'}
            dow_data = [{
                'day': day_names.get(r['_id'], str(r['_id'])),
                'total': r['total'],
                'no_shows': r['no_shows'],
                'rate': round(r['no_shows'] / max(r['total'], 1) * 100, 1),
            } for r in self.db['appointments'].aggregate(dow_pipe)]

            return {'by_department': dept_data, 'by_type': type_data, 'by_day': dow_data}
        except Exception as e:
            print(f'No-show analysis error: {e}')
            return {'by_department': [], 'by_type': [], 'by_day': []}
