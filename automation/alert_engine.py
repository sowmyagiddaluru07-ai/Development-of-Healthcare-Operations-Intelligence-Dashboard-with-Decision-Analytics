import logging
from datetime import datetime, timedelta
from bson.objectid import ObjectId
from config.settings import Settings

logger = logging.getLogger(__name__)

class AlertEngine:
    """Automated rule detection and operational alert manager."""

    def __init__(self, db):
        self.db = db
        self.col = self.db['operational_alerts']

    def _create_alert(self, alert_type, severity, title, message, facility_id=None, department_id=None, details=None):
        """Create an operational alert if duplicate active alert does not exist."""
        try:
            query = {
                'alert_type': alert_type,
                'status': 'Active'
            }
            if facility_id:
                query['facility_id'] = facility_id

            existing = self.col.find_one(query)
            if not existing:
                alert = {
                    'alert_id': f"ALT-{datetime.now().strftime('%Y%m%d%H%M%S')}-{random_str()}",
                    'alert_type': alert_type,
                    'severity': severity,
                    'title': title,
                    'message': message,
                    'facility_id': facility_id,
                    'department_id': department_id,
                    'status': 'Active',
                    'details': details or {},
                    'created_at': datetime.now(),
                    'updated_at': datetime.now()
                }
                res = self.col.insert_one(alert)
                return str(res.inserted_id)
            else:
                # Update timestamp on existing active alert without creating duplicate
                self.col.update_one({'_id': existing['_id']}, {'$set': {'updated_at': datetime.now()}})
                return str(existing['_id'])
        except Exception as e:
            logger.error(f"Error creating alert: {e}")
            return None

    def check_bed_capacity(self):
        """Check bed occupancy per facility against threshold (85%)."""
        results = []
        try:
            for fac in Settings.FACILITIES:
                fac_id = fac['id']
                total_beds = fac['beds']
                admitted = self.db['admissions'].count_documents({'facility_id': fac_id, 'status': 'Admitted'})
                occ_rate = (admitted / max(total_beds, 1)) * 100

                if occ_rate >= Settings.BED_OCCUPANCY_THRESHOLD:
                    self._create_alert(
                        alert_type='BED_CAPACITY_HIGH',
                        severity='HIGH' if occ_rate < 95 else 'CRITICAL',
                        title=f'High Bed Occupancy - {fac["name"]}',
                        message=f'Bed occupancy rate at {occ_rate:.1f}% ({admitted}/{total_beds} beds occupied).',
                        facility_id=fac_id,
                        details={'admitted': admitted, 'total_beds': total_beds, 'occupancy_rate': occ_rate}
                    )
                    results.append({'facility_id': fac_id, 'occupancy_rate': occ_rate})
            return results
        except Exception as e:
            logger.error(f"Error checking bed capacity: {e}")
            return []

    def check_pharmacy_stock(self):
        """Check pharmacy stock levels against reorder levels."""
        results = []
        try:
            low_stock = list(self.db['pharmacy_inventory'].find({
                "$expr": {"$lt": ["$stock_quantity", "$reorder_level"]}
            }))
            if low_stock:
                by_fac = {}
                for item in low_stock:
                    fac_id = item.get('facility_id', 'FAC001')
                    by_fac[fac_id] = by_fac.get(fac_id, 0) + 1

                for fac_id, count in by_fac.items():
                    self._create_alert(
                        alert_type='PHARMACY_STOCK_LOW',
                        severity='HIGH' if count > 5 else 'MEDIUM',
                        title='Low Pharmacy Inventory Stock',
                        message=f'{count} medication SKUs below reorder thresholds.',
                        facility_id=fac_id,
                        details={'low_stock_count': count}
                    )
                    results.append({'facility_id': fac_id, 'count': count})
            return results
        except Exception as e:
            logger.error(f"Error checking pharmacy stock: {e}")
            return []

    def check_waiting_times(self):
        """Check average appointment waiting times (>45 mins)."""
        results = []
        try:
            pipeline = [
                {"$group": {"_id": "$facility_id", "avg_wait": {"$avg": "$waiting_time_minutes"}}}
            ]
            res = list(self.db['appointments'].aggregate(pipeline))
            for item in res:
                fac_id = item['_id']
                avg_wait = item.get('avg_wait', 0)
                if fac_id and avg_wait >= Settings.WAITING_TIME_THRESHOLD:
                    self._create_alert(
                        alert_type='WAIT_TIME_EXCEEDED',
                        severity='MEDIUM' if avg_wait < 60 else 'HIGH',
                        title='Excessive Patient Wait Times',
                        message=f'Average waiting time is {avg_wait:.0f} minutes (threshold: {Settings.WAITING_TIME_THRESHOLD} mins).',
                        facility_id=fac_id,
                        details={'avg_waiting_time': avg_wait}
                    )
                    results.append({'facility_id': fac_id, 'avg_wait': avg_wait})
            return results
        except Exception as e:
            logger.error(f"Error checking wait times: {e}")
            return []

    def check_claim_aging(self):
        """Check pending insurance claim aging (>30 days)."""
        results = []
        try:
            thirty_days_ago = datetime.now() - timedelta(days=30)
            pending_old = self.db['insurance_claims'].count_documents({
                'status': 'Pending',
                'submission_date': {'$lt': thirty_days_ago}
            })
            if pending_old > 0:
                self._create_alert(
                    alert_type='CLAIMS_AGING_HIGH',
                    severity='HIGH' if pending_old > 100 else 'MEDIUM',
                    title='Unprocessed Insurance Claims Delay',
                    message=f'{pending_old} insurance claims pending over 30 days.',
                    facility_id='FAC001',
                    details={'pending_count': pending_old}
                )
                results.append({'pending_old': pending_old})
            return results
        except Exception as e:
            logger.error(f"Error checking claim aging: {e}")
            return []

    def check_staff_coverage(self):
        """Check active staff availability per facility."""
        results = []
        try:
            for fac in Settings.FACILITIES:
                fac_id = fac['id']
                count = self.db['staff'].count_documents({'facility_id': fac_id, 'status': 'Active'})
                if count < 15:
                    self._create_alert(
                        alert_type='STAFF_COVERAGE_LOW',
                        severity='HIGH',
                        title='Low Staff Coverage Warning',
                        message=f'Facility {fac["name"]} has only {count} active staff members.',
                        facility_id=fac_id,
                        details={'active_staff': count}
                    )
                    results.append({'facility_id': fac_id, 'count': count})
            return results
        except Exception as e:
            logger.error(f"Error checking staff coverage: {e}")
            return []

    def check_payment_aging(self):
        """Check overdue invoices (>60 days)."""
        results = []
        try:
            sixty_days_ago = datetime.now() - timedelta(days=60)
            overdue = self.db['billing'].count_documents({
                'payment_status': 'Overdue',
                'bill_date': {'$lt': sixty_days_ago}
            })
            if overdue > 0:
                self._create_alert(
                    alert_type='PAYMENT_OVERDUE_HIGH',
                    severity='HIGH' if overdue > 50 else 'MEDIUM',
                    title='Overdue AR Invoices Escalation',
                    message=f'{overdue} patient billing records overdue > 60 days.',
                    facility_id='FAC001',
                    details={'overdue_count': overdue}
                )
                results.append({'overdue_count': overdue})
            return results
        except Exception as e:
            logger.error(f"Error checking payment aging: {e}")
            return []

    def check_lab_delays(self):
        """Check pending lab tests (>24 hours)."""
        results = []
        try:
            twenty_four_hours_ago = datetime.now() - timedelta(hours=24)
            pending_lab = self.db['laboratory_tests'].count_documents({
                'status': 'Pending',
                'test_date': {'$lt': twenty_four_hours_ago}
            })
            if pending_lab > 0:
                self._create_alert(
                    alert_type='LAB_DELAY_HIGH',
                    severity='MEDIUM',
                    title='Delayed Laboratory Tests SLA',
                    message=f'{pending_lab} lab tests pending over 24 hours.',
                    facility_id='FAC001',
                    details={'pending_lab': pending_lab}
                )
                results.append({'pending_lab': pending_lab})
            return results
        except Exception as e:
            logger.error(f"Error checking lab delays: {e}")
            return []

    def run_all_checks(self):
        """Run all automated operational rule checks."""
        summary = {
            'bed_capacity': self.check_bed_capacity(),
            'pharmacy_stock': self.check_pharmacy_stock(),
            'claim_aging': self.check_claim_aging(),
            'waiting_times': self.check_waiting_times(),
            'staff_coverage': self.check_staff_coverage(),
            'payment_aging': self.check_payment_aging(),
            'lab_delays': self.check_lab_delays()
        }
        return summary

    def get_active_alerts(self, facility_id=None, severity=None, limit=None):
        """Query active operational alerts."""
        try:
            query = {'status': 'Active'}
            if facility_id:
                query['facility_id'] = facility_id
            if severity:
                query['severity'] = severity
                
            cursor = self.col.find(query).sort('created_at', -1)
            if limit:
                cursor = cursor.limit(limit)
                
            alerts = list(cursor)
            for a in alerts:
                a['_id'] = str(a['_id'])
                a['facility_id'] = str(a.get('facility_id', ''))
                if a.get('department_id'):
                    a['department_id'] = str(a['department_id'])
            return alerts
        except Exception as e:
            logger.error(f"Error getting active alerts: {e}")
            return []

    def get_alert_summary(self, facility_id=None):
        """Get summary count of active alerts by severity."""
        try:
            query = {'status': 'Active'}
            if facility_id:
                query['facility_id'] = facility_id
            total = self.col.count_documents(query)
            by_sev = {
                'CRITICAL': self.col.count_documents({**query, 'severity': 'CRITICAL'}),
                'HIGH': self.col.count_documents({**query, 'severity': 'HIGH'}),
                'MEDIUM': self.col.count_documents({**query, 'severity': 'MEDIUM'}),
                'LOW': self.col.count_documents({**query, 'severity': 'LOW'})
            }
            return {'total_active': total, 'by_severity': by_sev}
        except Exception as e:
            return {'total_active': 0, 'by_severity': {}}

    def resolve_alert(self, alert_id):
        """Mark an alert as resolved."""
        try:
            query = {'$or': [{'alert_id': alert_id}]}
            try:
                query['$or'].append({'_id': ObjectId(alert_id)})
            except Exception:
                pass
            res = self.col.update_one(query, {'$set': {'status': 'Resolved', 'updated_at': datetime.now()}})
            return res.modified_count > 0
        except Exception as e:
            logger.error(f"Error resolving alert: {e}")
            return False


def random_str(length=6):
    import random, string
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
