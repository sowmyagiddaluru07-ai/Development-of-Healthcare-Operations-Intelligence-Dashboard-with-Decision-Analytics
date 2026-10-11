from datetime import datetime, timedelta

class InsightsEngine:
    def __init__(self, db):
        self.db = db

    def generate_insights(self, facility_id=None):
        try:
            now = datetime.now()
            thirty_days_ago = now - timedelta(days=30)
            sixty_days_ago = now - timedelta(days=60)
            
            match_stage = {}
            if facility_id:
                match_stage['facility_id'] = facility_id
                
            insights = []
            
            # 1. Volume Trend
            vol_current = self._get_appointment_count(match_stage, thirty_days_ago, now)
            vol_prev = self._get_appointment_count(match_stage, sixty_days_ago, thirty_days_ago)
            
            if vol_prev > 0:
                diff_pct = ((vol_current - vol_prev) / vol_prev) * 100
                direction = "increased" if diff_pct > 0 else "decreased"
                insights.append(f"Appointment volume has {direction} by {abs(diff_pct):.1f}% in the last 30 days ({vol_current:,} vs {vol_prev:,} previous).")
            else:
                insights.append(f"Total appointments logged in last 30 days: {vol_current:,}.")
                
            # 2. Revenue Trend
            rev_current = self._get_revenue(match_stage, thirty_days_ago, now)
            rev_prev = self._get_revenue(match_stage, sixty_days_ago, thirty_days_ago)
            
            if rev_prev > 0:
                diff_pct = ((rev_current - rev_prev) / rev_prev) * 100
                direction = "increased" if diff_pct > 0 else "decreased"
                insights.append(f"Revenue collected has {direction} by {abs(diff_pct):.1f}% (${rev_current:,.2f} vs ${rev_prev:,.2f} previous).")
            else:
                insights.append(f"Total revenue collected in last 30 days: ${rev_current:,.2f}.")
                
            # 3. No Show Trend
            noshow_current = self._get_no_shows(match_stage, thirty_days_ago, now)
            noshow_prev = self._get_no_shows(match_stage, sixty_days_ago, thirty_days_ago)
            
            if vol_current > 0 and vol_prev > 0:
                rate_current = (noshow_current / vol_current) * 100
                rate_prev = (noshow_prev / vol_prev) * 100
                if rate_current > rate_prev + 2:
                    insights.append(f"⚠️ Warning: No-show rate increased from {rate_prev:.1f}% to {rate_current:.1f}%.")
                else:
                    insights.append(f"✅ No-show rate stands at {rate_current:.1f}% (previously {rate_prev:.1f}%).")
                    
            return insights
        except Exception as e:
            print(f"Error generating insights: {e}")
            return ["Unable to generate insights at this time."]

    def generate_daily_briefing(self, facility_id=None):
        try:
            today = datetime.now() - timedelta(days=30)
            
            match_stage = {}
            if facility_id:
                match_stage['facility_id'] = facility_id
                
            query = {"appointment_date": {"$gte": today}}
            query.update(match_stage)
            
            total_appts = self.db.appointments.count_documents(query)
            
            completed_query = {**query, "status": "Completed"}
            completed = self.db.appointments.count_documents(completed_query)
            
            noshow_query = {**query, "status": "No-show"}
            no_shows = self.db.appointments.count_documents(noshow_query)

            insights = self.generate_insights(facility_id=facility_id)
            
            text_summary = (
                f"**Daily Operations Executive Briefing ({datetime.now().strftime('%Y-%m-%d')})**\n\n"
                f"• **Total Scheduled/Processed Appointments:** {total_appts:,}\n"
                f"• **Completed Visits:** {completed:,} ({(completed/max(total_appts,1))*100:.1f}%)\n"
                f"• **No-Show Rate:** {(no_shows/max(total_appts,1))*100:.1f}%\n\n"
                f"**Key Operational Highlights:**\n"
            ) + "\n".join(f"- {i}" for i in insights)

            recommendations = [
                "Deploy automated SMS reminders 24 hours prior to appointment to reduce no-shows.",
                "Review peak hour staffing in Emergency & Cardiology departments.",
                "Follow up on pending insurance claims older than 30 days to optimize AR flow."
            ]

            return {
                'briefing': text_summary,
                'recommendations': recommendations,
                'total_scheduled': total_appts,
                'completed': completed,
                'no_shows': no_shows
            }
        except Exception as e:
            print(f"Error generating daily briefing: {e}")
            return {'briefing': f"Error generating briefing: {e}", 'recommendations': []}

    def _get_appointment_count(self, match_stage, start, end):
        query = {"appointment_date": {"$gte": start, "$lt": end}}
        query.update(match_stage)
        return self.db.appointments.count_documents(query)
        
    def _get_revenue(self, match_stage, start, end):
        query = {"bill_date": {"$gte": start, "$lt": end}}
        query.update(match_stage)
        pipeline = [
            {"$match": query},
            {"$group": {"_id": None, "total": {"$sum": "$net_amount"}}}
        ]
        res = list(self.db.billing.aggregate(pipeline))
        return res[0]['total'] if res else 0.0
        
    def _get_no_shows(self, match_stage, start, end):
        query = {"appointment_date": {"$gte": start, "$lt": end}, "status": "No-show"}
        query.update(match_stage)
        return self.db.appointments.count_documents(query)
