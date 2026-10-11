from datetime import datetime
from bson.objectid import ObjectId

class AuditLogger:
    def __init__(self, db):
        self.db = db

    def log(self, action, user_role='System', details=None, facility_id=None):
        try:
            log_entry = {
                'action': action,
                'user_role': user_role,
                'details': details or {},
                'facility_id': ObjectId(facility_id) if isinstance(facility_id, str) else facility_id,
                'timestamp': datetime.now()
            }
            result = self.db.audit_logs.insert_one(log_entry)
            return str(result.inserted_id)
        except Exception as e:
            print(f"Error creating audit log: {e}")
            return None

    def get_logs(self, limit=100, action=None):
        try:
            query = {}
            if action:
                query['action'] = action
                
            cursor = self.db.audit_logs.find(query).sort('timestamp', -1).limit(limit)
            logs = list(cursor)
            
            for log in logs:
                log['_id'] = str(log['_id'])
                if log.get('facility_id'):
                    log['facility_id'] = str(log['facility_id'])
            
            return logs
        except Exception as e:
            print(f"Error fetching audit logs: {e}")
            return []
