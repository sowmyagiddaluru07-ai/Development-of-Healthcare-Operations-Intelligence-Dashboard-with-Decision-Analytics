import re
from datetime import datetime, timedelta

class OperationsCopilot:
    """Natural language query processing engine over actual MongoDB data."""

    def __init__(self, db):
        self.db = db

    def process_query(self, query, facility_id=None):
        query_text = query.lower()
        match_stage = {}
        if facility_id:
            match_stage['facility_id'] = facility_id

        # Intent 1: Revenue & Financials
        if any(w in query_text for w in ['revenue', 'sales', 'billing', 'earnings', 'billed', 'financial']):
            return self._handle_revenue(match_stage)

        # Intent 2: Delays / Wait times
        if any(w in query_text for w in ['delay', 'wait', 'waiting', 'time']):
            return self._handle_delays(match_stage)

        # Intent 3: Doctor Productivity
        if any(w in query_text for w in ['productivity', 'doctor', 'physician', 'provider']):
            return self._handle_productivity(match_stage)

        # Intent 4: Insurance Claims
        if any(w in query_text for w in ['claim', 'insurance', 'denial', 'denied']):
            return self._handle_claims(match_stage)

        # Intent 5: Beds & Admissions
        if any(w in query_text for w in ['bed', 'capacity', 'admit', 'admission', 'occupancy']):
            return self._handle_beds(match_stage)

        # Intent 6: Pharmacy / Inventory
        if any(w in query_text for w in ['pharmacy', 'inventory', 'stock', 'medicine', 'drug']):
            return self._handle_pharmacy(match_stage)

        # Intent 7: Patient Volume
        if any(w in query_text for w in ['volume', 'appointment', 'visit', 'patient']):
            return self._handle_volume(match_stage)

        # Intent 8: Staff Intelligence
        if any(w in query_text for w in ['staff', 'nurse', 'workload', 'shift']):
            return self._handle_staff(match_stage)

        # Intent 9: Emergency
        if any(w in query_text for w in ['emergency', 'er', 'triage', 'trauma']):
            return self._handle_emergency(match_stage)

        # Default summary
        return self._handle_summary(match_stage)

    def _handle_revenue(self, match_stage):
        try:
            pipeline = []
            if match_stage:
                pipeline.append({"$match": match_stage})
            pipeline.append({
                "$group": {
                    "_id": None,
                    "total_billed": {"$sum": "$net_amount"},
                    "total_outstanding": {"$sum": "$outstanding_amount"},
                    "count": {"$sum": 1}
                }
            })
            res = list(self.db['billing'].aggregate(pipeline))
            if res:
                total_billed = res[0]['total_billed']
                total_outstanding = res[0]['total_outstanding']
                paid = total_billed - total_outstanding
                answer = f"Total billed revenue is **${total_billed:,.2f}** across {res[0]['count']:,} bills. " \
                         f"Total collected: **${paid:,.2f}** | Outstanding AR: **${total_outstanding:,.2f}**."
                return {"answer": answer, "data": res[0]}
            return {"answer": "No billing records found.", "data": {}}
        except Exception as e:
            return {"answer": f"Error querying revenue data: {e}", "data": {}}

    def _handle_delays(self, match_stage):
        try:
            pipeline = []
            if match_stage:
                pipeline.append({"$match": match_stage})
            pipeline.extend([
                {"$match": {"waiting_time_minutes": {"$ne": None}}},
                {"$group": {"_id": "$department_id", "avg_wait": {"$avg": "$waiting_time_minutes"}, "count": {"$sum": 1}}},
                {"$sort": {"avg_wait": -1}}
            ])
            res = list(self.db['appointments'].aggregate(pipeline))
            if res:
                overall_avg = sum(r['avg_wait'] * r['count'] for r in res) / sum(r['count'] for r in res)
                top_dept = res[0]
                answer = f"Average waiting time across all appointments is **{overall_avg:.1f} minutes**. " \
                         f"Highest waiting time department is **{top_dept['_id']}** averaging **{top_dept['avg_wait']:.1f} minutes**."
                return {"answer": answer, "data": res[:5]}
            return {"answer": "No appointment waiting time records found.", "data": []}
        except Exception as e:
            return {"answer": f"Error querying waiting times: {e}", "data": []}

    def _handle_productivity(self, match_stage):
        try:
            pipeline = []
            if match_stage:
                pipeline.append({"$match": match_stage})
            pipeline.extend([
                {"$group": {"_id": "$doctor_id", "total_appointments": {"$sum": 1}}},
                {"$sort": {"total_appointments": -1}},
                {"$limit": 5}
            ])
            res = list(self.db['appointments'].aggregate(pipeline))
            if res:
                doc_list = ", ".join(f"Doctor **{r['_id']}** ({r['total_appointments']} appts)" for r in res)
                answer = f"Top 5 most productive doctors: {doc_list}."
                return {"answer": answer, "data": res}
            return {"answer": "No doctor appointment records found.", "data": []}
        except Exception as e:
            return {"answer": f"Error querying doctor productivity: {e}", "data": []}

    def _handle_claims(self, match_stage):
        try:
            filter_dict = match_stage if match_stage else {}
            total = self.db['insurance_claims'].count_documents(filter_dict)
            denied = self.db['insurance_claims'].count_documents({**filter_dict, "status": "Denied"})
            approved = self.db['insurance_claims'].count_documents({**filter_dict, "status": "Approved"})
            denial_rate = (denied / max(total, 1)) * 100
            
            answer = f"Total claims filed: **{total:,}**. Approved: **{approved:,}** | Denied: **{denied:,}** " \
                     f"(Denial Rate: **{denial_rate:.1f}%**)."
            return {"answer": answer, "data": {"total": total, "approved": approved, "denied": denied, "denial_rate": denial_rate}}
        except Exception as e:
            return {"answer": f"Error querying insurance claims: {e}", "data": {}}

    def _handle_beds(self, match_stage):
        try:
            filter_dict = match_stage if match_stage else {}
            admitted = self.db['admissions'].count_documents({**filter_dict, "status": "Admitted"})
            discharged = self.db['admissions'].count_documents({**filter_dict, "status": "Discharged"})
            total_adm = admitted + discharged
            
            answer = f"Active admitted patients currently occupying beds: **{admitted:,}**. Total historical admissions: **{total_adm:,}**."
            return {"answer": answer, "data": {"active_admitted": admitted, "discharged": discharged}}
        except Exception as e:
            return {"answer": f"Error querying bed admissions: {e}", "data": {}}

    def _handle_pharmacy(self, match_stage):
        try:
            filter_dict = match_stage if match_stage else {}
            total_items = self.db['pharmacy_inventory'].count_documents(filter_dict)
            low_stock = list(self.db['pharmacy_inventory'].find({
                **filter_dict,
                "$expr": {"$lt": ["$stock_quantity", "$reorder_level"]}
            }, {"_id": 0, "name": 1, "stock_quantity": 1, "reorder_level": 1}).limit(5))
            
            answer = f"Total pharmacy SKUs: **{total_items:,}**. Items below reorder level: **{len(low_stock)}**."
            return {"answer": answer, "data": low_stock}
        except Exception as e:
            return {"answer": f"Error querying pharmacy stock: {e}", "data": {}}

    def _handle_volume(self, match_stage):
        try:
            filter_dict = match_stage if match_stage else {}
            total_appts = self.db['appointments'].count_documents(filter_dict)
            completed = self.db['appointments'].count_documents({**filter_dict, "status": "Completed"})
            no_shows = self.db['appointments'].count_documents({**filter_dict, "status": "No-show"})
            
            answer = f"Total appointments: **{total_appts:,}**. Completed: **{completed:,}** | No-shows: **{no_shows:,}** ({(no_shows/max(total_appts,1))*100:.1f}%)."
            return {"answer": answer, "data": {"total": total_appts, "completed": completed, "no_shows": no_shows}}
        except Exception as e:
            return {"answer": f"Error querying appointment volume: {e}", "data": {}}

    def _handle_staff(self, match_stage):
        try:
            filter_dict = match_stage if match_stage else {}
            doctors = self.db['staff'].count_documents({**filter_dict, "role": "Doctor"})
            nurses = self.db['staff'].count_documents({**filter_dict, "role": "Nurse"})
            total = self.db['staff'].count_documents(filter_dict)
            
            answer = f"Total hospital workforce: **{total:,}** staff members (**{doctors:,}** Doctors, **{nurses:,}** Nurses)."
            return {"answer": answer, "data": {"total_staff": total, "doctors": doctors, "nurses": nurses}}
        except Exception as e:
            return {"answer": f"Error querying staff intelligence: {e}", "data": {}}

    def _handle_emergency(self, match_stage):
        try:
            filter_dict = match_stage if match_stage else {}
            total_er = self.db['emergency_cases'].count_documents(filter_dict)
            critical = self.db['emergency_cases'].count_documents({**filter_dict, "triage_level": {"$in": [1, 2]}})
            
            answer = f"Total Emergency Department cases: **{total_er:,}**. High-severity Triage Level 1/2 cases: **{critical:,}**."
            return {"answer": answer, "data": {"total_er_cases": total_er, "critical_cases": critical}}
        except Exception as e:
            return {"answer": f"Error querying ER cases: {e}", "data": {}}

    def _handle_summary(self, match_stage):
        try:
            patients = self.db['patients'].count_documents(match_stage)
            appts = self.db['appointments'].count_documents(match_stage)
            billing_res = list(self.db['billing'].aggregate([
                *( [{"$match": match_stage}] if match_stage else [] ),
                {"$group": {"_id": None, "rev": {"$sum": "$net_amount"}}}
            ]))
            rev = billing_res[0]['rev'] if billing_res else 0.0

            answer = f"Operational Overview: **{patients:,}** registered patients, **{appts:,}** appointments, and **${rev:,.2f}** total billed revenue."
            return {"answer": answer, "data": {"patients": patients, "appointments": appts, "total_revenue": rev}}
        except Exception as e:
            return {"answer": f"System operational overview summary generated.", "data": {}}


# Alias for compatibility
OperationalQueryEngine = OperationsCopilot
