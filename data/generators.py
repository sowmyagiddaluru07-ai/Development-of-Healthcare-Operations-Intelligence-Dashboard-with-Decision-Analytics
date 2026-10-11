import random
from datetime import datetime, timedelta

FACILITIES = [
    {'id': 'FAC001', 'name': 'Central Hospital', 'beds': 500},
    {'id': 'FAC002', 'name': 'City Care Hospital', 'beds': 300},
    {'id': 'FAC003', 'name': 'North Branch', 'beds': 150},
    {'id': 'FAC004', 'name': 'South Branch', 'beds': 150},
]
DEPARTMENTS = [
    {'id': 'DEP001', 'name': 'Emergency'},
    {'id': 'DEP002', 'name': 'Cardiology'},
    {'id': 'DEP003', 'name': 'Neurology'},
    {'id': 'DEP004', 'name': 'Orthopedics'},
    {'id': 'DEP005', 'name': 'Pediatrics'},
    {'id': 'DEP006', 'name': 'General Medicine'},
    {'id': 'DEP007', 'name': 'Surgery'},
    {'id': 'DEP008', 'name': 'ICU'},
    {'id': 'DEP009', 'name': 'Dermatology'},
    {'id': 'DEP010', 'name': 'Gynecology'},
]

FIRST_NAMES = [
    'James', 'Mary', 'Robert', 'Patricia', 'John', 'Jennifer', 'Michael', 'Linda',
    'William', 'Elizabeth', 'David', 'Barbara', 'Richard', 'Susan', 'Joseph', 'Jessica',
    'Thomas', 'Sarah', 'Charles', 'Karen', 'Christopher', 'Nancy', 'Daniel', 'Lisa',
    'Matthew', 'Betty', 'Anthony', 'Margaret', 'Mark', 'Sandra', 'Donald', 'Ashley',
    'Steven', 'Kimberly', 'Paul', 'Emily', 'Andrew', 'Donna', 'Joshua', 'Michelle',
    'Kenneth', 'Dorothy', 'Kevin', 'Carol', 'Brian', 'Amanda', 'George', 'Melissa',
    'Edward', 'Deborah', 'Ronald', 'Stephanie', 'Timothy', 'Rebecca', 'Jason', 'Sharon',
    'Jeffrey', 'Laura', 'Ryan', 'Cynthia', 'Jacob', 'Kathleen', 'Gary', 'Amy', 'Nicholas',
    'Shirley', 'Eric', 'Angela', 'Jonathan', 'Helen', 'Stephen', 'Anna', 'Larry', 'Brenda',
    'Justin', 'Pamela', 'Scott', 'Nicole', 'Brandon', 'Emma', 'Benjamin', 'Samantha',
    'Samuel', 'Katherine', 'Gregory', 'Christine', 'Frank', 'Debra', 'Alexander', 'Rachel',
    'Raymond', 'Catherine', 'Patrick', 'Carolyn', 'Jack', 'Janet', 'Dennis', 'Ruth',
    'Jerry', 'Maria', 'Tyler', 'Heather', 'Aaron', 'Diane'
]

LAST_NAMES = [
    'Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis',
    'Rodriguez', 'Martinez', 'Hernandez', 'Lopez', 'Gonzalez', 'Wilson', 'Anderson',
    'Thomas', 'Taylor', 'Moore', 'Jackson', 'Martin', 'Lee', 'Perez', 'Thompson',
    'White', 'Harris', 'Sanchez', 'Clark', 'Ramirez', 'Lewis', 'Robinson', 'Walker',
    'Young', 'Allen', 'King', 'Wright', 'Scott', 'Torres', 'Nguyen', 'Hill', 'Flores',
    'Green', 'Adams', 'Nelson', 'Baker', 'Hall', 'Rivera', 'Campbell', 'Mitchell',
    'Carter', 'Roberts', 'Gomez', 'Phillips', 'Evans', 'Turner', 'Diaz', 'Parker',
    'Cruz', 'Edwards', 'Collins', 'Reyes', 'Stewart', 'Morris', 'Morales', 'Murphy',
    'Cook', 'Rogers', 'Gutierrez', 'Ortiz', 'Morgan', 'Cooper', 'Peterson', 'Bailey',
    'Reed', 'Kelly', 'Howard', 'Ramos', 'Kim', 'Cox', 'Ward', 'Richardson'
]

MEDICINES = [
    'Amoxicillin', 'Ibuprofen', 'Metformin', 'Lisinopril', 'Amlodipine', 
    'Atorvastatin', 'Omeprazole', 'Losartan', 'Metoprolol', 'Levothyroxine', 
    'Azithromycin', 'Ciprofloxacin', 'Prednisone', 'Gabapentin', 'Sertraline', 
    'Escitalopram', 'Fluoxetine', 'Pantoprazole', 'Clopidogrel', 'Warfarin', 
    'Aspirin', 'Acetaminophen', 'Diclofenac', 'Ranitidine', 'Cetirizine', 
    'Montelukast', 'Salbutamol', 'Insulin Glargine', 'Methotrexate', 'Furosemide', 
    'Hydrochlorothiazide', 'Propranolol', 'Atenolol', 'Ramipril', 'Doxycycline', 
    'Ceftriaxone', 'Clindamycin', 'Vancomycin', 'Morphine', 'Tramadol', 
    'Fentanyl', 'Diazepam', 'Lorazepam', 'Midazolam', 'Ondansetron', 
    'Epinephrine', 'Heparin', 'Enoxaparin', 'Mannitol', 'Dopamine'
]

class SyntheticDataGenerator:
    def __init__(self):
        random.seed(42)
        self.now = datetime.now()
        self.start_date = self.now - timedelta(days=180) # 6 months historical data

    def random_date(self, start, end):
        return start + timedelta(seconds=random.randint(0, int((end - start).total_seconds())))

    def generate_patients(self, n=5000):
        patients = []
        for i in range(1, n + 1):
            dob = self.random_date(self.now - timedelta(days=365*90), self.now - timedelta(days=365))
            age = (self.now - dob).days // 365
            age_group = '0-17' if age <= 17 else '18-30' if age <= 30 else '31-45' if age <= 45 else '46-60' if age <= 60 else '61+'
            
            patients.append({
                'patient_id': f'PAT{i:05d}',
                'first_name': random.choice(FIRST_NAMES),
                'last_name': random.choice(LAST_NAMES),
                'gender': random.choices(['Male', 'Female', 'Other'], weights=[48, 48, 4])[0],
                'date_of_birth': dob,
                'age': age,
                'demographics': {
                    'age_group': age_group,
                    'blood_group': random.choice(['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']),
                    'insurance_status': random.choices(['Active', 'Expired', 'None'], weights=[70, 10, 20])[0]
                },
                'contact': {
                    'phone': f"{random.randint(100,999)}-{random.randint(100,999)}-{random.randint(1000,9999)}",
                    'email': f"user{i}@example.com",
                    'address': f"{random.randint(1,9999)} Main St",
                    'city': "Metropolis",
                    'state': "ST",
                    'zip_code': f"{random.randint(10000,99999)}"
                },
                'facility_id': random.choices(['FAC001', 'FAC002', 'FAC003', 'FAC004'], weights=[40, 30, 15, 15])[0],
                'registration_date': self.random_date(self.now - timedelta(days=730), self.now),
                'status': random.choices(['Active', 'Inactive'], weights=[90, 10])[0],
                'medical_record_number': f'MRN{i:06d}'
            })
        return patients

    def generate_staff(self, n=120):
        staff = []
        roles = ['Doctor', 'Nurse', 'Technician', 'Admin', 'Pharmacist']
        weights = [40, 40, 20, 10, 10]
        
        for i in range(1, n + 1):
            role = random.choices(roles, weights=weights)[0]
            department = random.choice(DEPARTMENTS)
            spec = department['name'] if role == 'Doctor' else 'General'
            
            base_rate = {'Doctor': 150, 'Nurse': 70, 'Technician': 60, 'Admin': 50, 'Pharmacist': 80}[role]
            
            staff.append({
                'staff_id': f'STF{i:03d}',
                'first_name': random.choice(FIRST_NAMES),
                'last_name': random.choice(LAST_NAMES),
                'role': role,
                'specialization': spec,
                'department_id': department['id'],
                'facility_id': random.choice(FACILITIES)['id'],
                'hire_date': self.random_date(self.now - timedelta(days=365*10), self.now - timedelta(days=30)),
                'status': random.choices(['Active', 'On Leave'], weights=[95, 5])[0],
                'shift': random.choice(['Morning', 'Afternoon', 'Night']),
                'hourly_rate': base_rate + random.randint(-10, 50),
                'weekly_hours': random.randint(36, 48),
                'overtime_hours': random.randint(11, 20) if random.random() < 0.2 else random.randint(0, 10),
                'utilization_rate': round(random.uniform(0.4, 0.95), 2),
                'contact': {
                    'phone': f"{random.randint(100,999)}-{random.randint(100,999)}-{random.randint(1000,9999)}",
                    'email': f"staff{i}@hospital.com"
                }
            })
        return staff

    def generate_appointments(self, n=12000, patients=[], staff=[]):
        appointments = []
        doctors = [s for s in staff if s['role'] == 'Doctor']
        if not doctors: return appointments
        
        for i in range(1, n + 1):
            patient = random.choice(patients)
            doctor = random.choice(doctors)
            
            # More weekdays
            appt_date = self.random_date(self.start_date, self.now)
            while appt_date.weekday() >= 5 and random.random() < 0.7:
                appt_date = self.random_date(self.start_date, self.now)
                
            status = random.choices(['Completed', 'Scheduled', 'Cancelled', 'No-show'], weights=[65, 10, 12, 13])[0]
            if appt_date > self.now:
                status = 'Scheduled'
                
            hour = random.randint(8, 17)
            minute = random.choice([0, 15, 30, 45])
            sched_time = f"{hour:02d}:{minute:02d}"
            
            delay = random.randint(0, 45)
            waiting_time = random.randint(5, 90)
            
            appointments.append({
                'appointment_id': f'APT{i:05d}',
                'patient_id': patient['patient_id'],
                'doctor_id': doctor['staff_id'],
                'department_id': doctor['department_id'],
                'facility_id': doctor['facility_id'],
                'appointment_date': appt_date,
                'appointment_type': random.choice(['Consultation', 'Follow-up', 'Procedure', 'Emergency', 'Routine']),
                'status': status,
                'scheduled_time': sched_time,
                'actual_start_time': (appt_date + timedelta(minutes=delay)).strftime('%H:%M'),
                'waiting_time_minutes': waiting_time,
                'duration_minutes': random.randint(15, 120),
                'notes': 'Generated note'
            })
        return appointments

    def generate_admissions(self, n=5000, patients=[], staff=[]):
        admissions = []
        doctors = [s for s in staff if s['role'] == 'Doctor']
        if not doctors: return admissions
        
        for i in range(1, n + 1):
            patient = random.choice(patients)
            doctor = random.choice(doctors)
            
            admin_date = self.random_date(self.start_date, self.now)
            los = random.randint(1, 14)
            
            disch_date = admin_date + timedelta(days=los)
            status = 'Discharged'
            if random.random() < 0.05:
                disch_date = None
                status = 'Admitted'
                
            admissions.append({
                'admission_id': f'ADM{i:05d}',
                'patient_id': patient['patient_id'],
                'doctor_id': doctor['staff_id'],
                'department_id': doctor['department_id'],
                'facility_id': doctor['facility_id'],
                'admission_date': admin_date,
                'discharge_date': disch_date,
                'admission_type': random.choice(['Emergency', 'Planned', 'Transfer']),
                'bed_number': f"B{random.randint(100, 999)}",
                'status': status,
                'length_of_stay_days': los if disch_date else None,
                'diagnosis_category': random.choice(['Cardiovascular', 'Respiratory', 'Neurological', 'Orthopedic', 'General']),
                'is_readmission': random.random() < 0.15,
                'readmission_within_30_days': random.random() < 0.05
            })
        return admissions

    def generate_billing(self, n=8000, patients=[], staff=[]):
        billing = []
        doctors = [s for s in staff if s['role'] == 'Doctor']
        if not doctors: return billing
        
        for i in range(1, n + 1):
            patient = random.choice(patients)
            doctor = random.choice(doctors)
            
            total_amount = round(random.uniform(100, 5000), 2)
            discount = round(total_amount * random.uniform(0, 0.2), 2)
            tax = round((total_amount - discount) * 0.08, 2)
            net = round(total_amount - discount + tax, 2)
            
            status = random.choice(['Paid', 'Partial', 'Pending', 'Overdue'])
            out_amount = 0 if status == 'Paid' else net if status in ('Pending', 'Overdue') else round(net / 2, 2)
            
            billing.append({
                'bill_id': f'BIL{i:05d}',
                'patient_id': patient['patient_id'],
                'doctor_id': doctor['staff_id'],
                'department_id': doctor['department_id'],
                'facility_id': doctor['facility_id'],
                'bill_date': self.random_date(self.start_date, self.now),
                'total_amount': total_amount,
                'discount': discount,
                'tax': tax,
                'net_amount': net,
                'payment_status': status,
                'payment_method': random.choice(['Credit Card', 'Cash', 'Insurance', 'Bank Transfer']),
                'payment_date': self.random_date(self.start_date, self.now) if status in ('Paid', 'Partial') else None,
                'outstanding_amount': out_amount,
                'billing_category': random.choice(['Consultation', 'Procedure', 'Pharmacy', 'Lab', 'Room'])
            })
        return billing

    def generate_insurance_claims(self, n=5000, patients=[]):
        claims = []
        payers = ['BlueCross', 'Medicare', 'Aetna', 'Cigna', 'UnitedHealth']
        
        for i in range(1, n + 1):
            patient = random.choice(patients)
            sub_date = self.random_date(self.start_date, self.now - timedelta(days=30))
            status = random.choice(['Approved', 'Pending', 'Denied', 'Under Review'])
            claim_amt = round(random.uniform(200, 10000), 2)
            appr_amt = round(claim_amt * random.uniform(0.5, 1.0), 2) if status == 'Approved' else 0.0
            
            claims.append({
                'claim_id': f'CLM{i:05d}',
                'patient_id': patient['patient_id'],
                'bill_id': f'BIL{random.randint(1, 8000):05d}',
                'payer': random.choice(payers),
                'policy_number': f"POL{random.randint(100000, 999999)}",
                'claim_amount': claim_amt,
                'approved_amount': appr_amt,
                'status': status,
                'submission_date': sub_date,
                'processing_date': sub_date + timedelta(days=random.randint(5, 45)) if status in ('Approved', 'Denied') else None,
                'denial_reason': random.choice(['Coverage Lapsed', 'Not Covered', 'Missing Info']) if status == 'Denied' else None,
                'claim_age_days': (self.now - sub_date).days,
                'facility_id': random.choice(FACILITIES)['id'],
                'department_id': random.choice(DEPARTMENTS)['id']
            })
        return claims

    def generate_medical_coding(self, n=3000):
        coding = []
        for i in range(1, n + 1):
            coding.append({
                'coding_id': f'COD{i:05d}',
                'bill_id': f'BIL{random.randint(1, 8000):05d}',
                'icd_code': f"{random.choice(['A', 'B', 'C', 'I', 'J'])}{random.randint(10, 99)}.{random.randint(0, 9)}",
                'cpt_code': f"{random.randint(10000, 99999)}",
                'coder_id': f'STF{random.randint(1, 120):03d}',
                'coding_date': self.random_date(self.start_date, self.now),
                'status': random.choice(['Completed', 'Pending Audit', 'Audited']),
                'documentation_completeness': random.randint(60, 100),
                'coding_accuracy': random.randint(70, 100),
                'has_error': random.random() < 0.1,
                'error_type': random.choice(['Wrong Code', 'Missing Modifier', 'Upcoding']) if random.random() < 0.1 else None
            })
        return coding

    def generate_pharmacy_inventory(self, n=250):
        inventory = []
        for i in range(1, n + 1):
            stock = random.randint(0, 1000)
            status = 'Out of Stock' if stock == 0 else 'Low Stock' if stock < 100 else 'In Stock'
            inventory.append({
                'medicine_id': f'MED{i:03d}',
                'name': MEDICINES[i % len(MEDICINES)],
                'category': random.choice(['Antibiotic', 'Painkiller', 'Cardiovascular', 'Endocrine', 'Psychiatric']),
                'unit_price': round(random.uniform(1.0, 150.0), 2),
                'stock_quantity': stock,
                'reorder_level': random.randint(50, 200),
                'max_stock': random.randint(500, 2000),
                'facility_id': random.choice(FACILITIES)['id'],
                'vendor_id': f'VEN{random.randint(1, 30):03d}',
                'expiry_date': self.now + timedelta(days=random.randint(10, 730)),
                'last_restock_date': self.random_date(self.now - timedelta(days=90), self.now),
                'daily_consumption_rate': round(random.uniform(1, 50), 1),
                'status': status
            })
            if inventory[-1]['expiry_date'] < self.now + timedelta(days=30):
                inventory[-1]['status'] = 'Near Expiry'
        return inventory

    def generate_laboratory_tests(self, n=6000, patients=[], staff=[]):
        tests = []
        doctors = [s for s in staff if s['role'] == 'Doctor']
        if not doctors: return tests
        
        for i in range(1, n + 1):
            test_date = self.random_date(self.start_date, self.now)
            tests.append({
                'test_id': f'LAB{i:05d}',
                'patient_id': random.choice(patients)['patient_id'],
                'doctor_id': random.choice(doctors)['staff_id'],
                'facility_id': random.choice(FACILITIES)['id'],
                'department_id': random.choice(DEPARTMENTS)['id'],
                'test_name': random.choice(['Complete Blood Count', 'Lipid Panel', 'Thyroid Panel', 'HbA1c', 'Urinalysis']),
                'test_category': random.choice(['Hematology', 'Biochemistry', 'Microbiology', 'Pathology']),
                'test_date': test_date,
                'sample_collection_time': test_date,
                'result_time': test_date + timedelta(hours=random.randint(1, 48)),
                'turnaround_hours': random.randint(1, 48),
                'status': random.choice(['Completed', 'Pending', 'In Progress', 'Cancelled']),
                'priority': random.choice(['Routine', 'Urgent', 'STAT']),
                'equipment_id': f'EQP{random.randint(1, 50):03d}',
                'technician_id': f'STF{random.randint(1, 120):03d}',
                'cost': round(random.uniform(20, 500), 2)
            })
        return tests

    def generate_emergency_cases(self, n=2500, patients=[], staff=[]):
        cases = []
        doctors = [s for s in staff if s['role'] == 'Doctor']
        if not doctors: return cases
        
        for i in range(1, n + 1):
            triage = random.randint(1, 5)
            wait_time = max(0, (triage - 1) * 15 + random.randint(-10, 20))
            arrival = self.random_date(self.start_date, self.now)
            
            cases.append({
                'case_id': f'EMG{i:05d}',
                'patient_id': random.choice(patients)['patient_id'],
                'facility_id': random.choice(FACILITIES)['id'],
                'arrival_time': arrival,
                'triage_level': triage,
                'chief_complaint': random.choice(['Chest Pain', 'Shortness of Breath', 'Fever', 'Trauma', 'Abdominal Pain']),
                'attending_doctor_id': random.choice(doctors)['staff_id'],
                'treatment_start_time': arrival + timedelta(minutes=wait_time),
                'waiting_time_minutes': wait_time,
                'treatment_duration_minutes': random.randint(30, 240),
                'disposition': random.choice(['Admitted', 'Discharged', 'Transferred', 'Left Without Being Seen']),
                'bed_assigned': f"ER-B{random.randint(1, 50)}",
                'staff_count': random.randint(1, 5),
                'status': random.choice(['Active', 'Closed'])
            })
        return cases

    def generate_quality_incidents(self, n=600):
        incidents = []
        for i in range(1, n + 1):
            rep_date = self.random_date(self.start_date, self.now)
            status = random.choice(['Open', 'In Progress', 'Resolved', 'Closed'])
            res_date = rep_date + timedelta(days=random.randint(1, 30)) if status in ('Resolved', 'Closed') else None
            
            incidents.append({
                'incident_id': f'QI{i:04d}',
                'facility_id': random.choice(FACILITIES)['id'],
                'department_id': random.choice(DEPARTMENTS)['id'],
                'incident_type': random.choice(['Medication Error', 'Patient Fall', 'Equipment Failure', 'Delay in Care']),
                'severity': random.choice(['Low', 'Medium', 'High', 'Critical']),
                'reported_date': rep_date,
                'reported_by': f'STF{random.randint(1, 120):03d}',
                'status': status,
                'resolution_date': res_date,
                'corrective_action': 'Action documented' if res_date else None,
                'root_cause': random.choice(['Process Failure', 'Human Error', 'System Issue']) if res_date else None,
                'days_to_resolve': (res_date - rep_date).days if res_date else None,
                'sop_adherence': random.random() > 0.3
            })
        return incidents

    def generate_patient_feedback(self, n=3500, patients=[]):
        feedback = []
        for i in range(1, n + 1):
            rating = random.randint(1, 5)
            sentiment = 'Positive' if rating >= 4 else 'Neutral' if rating == 3 else 'Negative'
            feedback.append({
                'feedback_id': f'FB{i:05d}',
                'patient_id': random.choice(patients)['patient_id'],
                'facility_id': random.choice(FACILITIES)['id'],
                'department_id': random.choice(DEPARTMENTS)['id'],
                'feedback_date': self.random_date(self.start_date, self.now),
                'rating': rating,
                'category': random.choice(['Care Quality', 'Wait Time', 'Facility Cleanliness', 'Staff Behavior']),
                'sentiment': sentiment,
                'comments': 'Sample comment based on experience.',
                'nps_score': rating * 2,
                'would_recommend': rating >= 4,
                'complaint_status': random.choice(['Resolved', 'Pending']) if rating <= 2 else None,
                'resolution_days': random.randint(1, 14) if rating <= 2 else None
            })
        return feedback

    def generate_vendors(self, n=30):
        vendors = []
        for i in range(1, n + 1):
            vendors.append({
                'vendor_id': f'VEN{i:03d}',
                'name': f'Vendor Corp {i}',
                'category': random.choice(['Pharmaceuticals', 'Equipment', 'Consumables', 'Services']),
                'contact': {
                    'phone': f"{random.randint(100,999)}-555-{random.randint(1000,9999)}",
                    'email': f"contact@vendor{i}.com"
                },
                'address': f"{random.randint(10, 999)} Commerce Way",
                'status': random.choice(['Active', 'Inactive', 'Under Review']),
                'rating': round(random.uniform(2.0, 5.0), 1),
                'delivery_reliability': round(random.uniform(0.7, 1.0), 2),
                'payment_terms': random.choice(['Net 30', 'Net 60', 'Due on Receipt']),
                'contract_start': self.now - timedelta(days=random.randint(100, 1000)),
                'contract_end': self.now + timedelta(days=random.randint(100, 1000))
            })
        return vendors

    def generate_purchase_orders(self, n=1200):
        pos = []
        for i in range(1, n + 1):
            order_date = self.random_date(self.start_date, self.now)
            exp_delivery = order_date + timedelta(days=random.randint(5, 30))
            status = random.choice(['Delivered', 'Pending', 'Cancelled'])
            act_delivery = exp_delivery + timedelta(days=random.randint(-2, 10)) if status == 'Delivered' else None
            
            pos.append({
                'po_id': f'PO{i:05d}',
                'vendor_id': f'VEN{random.randint(1, 30):03d}',
                'facility_id': random.choice(FACILITIES)['id'],
                'order_date': order_date,
                'expected_delivery': exp_delivery,
                'actual_delivery': act_delivery,
                'items': [{'item': f'Item{random.randint(1, 100)}', 'qty': random.randint(10, 1000)}],
                'total_amount': round(random.uniform(500, 50000), 2),
                'status': status,
                'delivery_delay_days': (act_delivery - exp_delivery).days if act_delivery and act_delivery > exp_delivery else 0,
                'payment_status': random.choice(['Paid', 'Pending'])
            })
        return pos

    def generate_financial_transactions(self, n=6000):
        txns = []
        for i in range(1, n + 1):
            tx_type = random.choice(['Revenue', 'Expense'])
            cat = random.choice(['Patient Billing', 'Grants', 'Investments']) if tx_type == 'Revenue' else random.choice(['Payroll', 'Supplies', 'Maintenance', 'Utilities'])
            amt = round(random.uniform(100, 20000), 2)
            txns.append({
                'transaction_id': f'FT{i:05d}',
                'facility_id': random.choice(FACILITIES)['id'],
                'department_id': random.choice(DEPARTMENTS)['id'],
                'transaction_date': self.random_date(self.start_date, self.now),
                'type': tx_type,
                'category': cat,
                'amount': amt,
                'description': f"{tx_type} for {cat}",
                'budget_amount': amt * round(random.uniform(0.9, 1.2), 2)
            })
        return txns

    def generate_all(self):
        patients = self.generate_patients()
        staff = self.generate_staff()
        appointments = self.generate_appointments(patients=patients, staff=staff)
        admissions = self.generate_admissions(patients=patients, staff=staff)
        billing = self.generate_billing(patients=patients, staff=staff)
        insurance = self.generate_insurance_claims(patients=patients)
        coding = self.generate_medical_coding()
        inventory = self.generate_pharmacy_inventory()
        labs = self.generate_laboratory_tests(patients=patients, staff=staff)
        emergencies = self.generate_emergency_cases(patients=patients, staff=staff)
        incidents = self.generate_quality_incidents()
        feedback = self.generate_patient_feedback(patients=patients)
        vendors = self.generate_vendors()
        pos = self.generate_purchase_orders()
        financials = self.generate_financial_transactions()
        
        return {
            'patients': patients,
            'staff': staff,
            'appointments': appointments,
            'admissions': admissions,
            'billing': billing,
            'insurance_claims': insurance,
            'medical_coding': coding,
            'pharmacy_inventory': inventory,
            'laboratory_tests': labs,
            'emergency_cases': emergencies,
            'quality_incidents': incidents,
            'patient_feedback': feedback,
            'vendors': vendors,
            'purchase_orders': pos,
            'financial_transactions': financials
        }
