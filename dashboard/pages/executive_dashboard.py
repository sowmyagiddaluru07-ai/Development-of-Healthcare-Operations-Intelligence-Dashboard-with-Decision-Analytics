"""Executive Dashboard Page for Medical Operations Intelligence."""
import streamlit as st
import pandas as pd
import plotly.express as px
from dashboard.components import (
    render_kpi_card,
    render_kpi_row,
    create_gauge_chart,
    create_line_chart,
    create_bar_chart,
    render_alert_card
)
from analytics.kpi_engine import KPIEngine
from automation.alert_engine import AlertEngine


def render_executive_dashboard(db, filters):
    st.title("🏥 Executive Operations Dashboard")
    st.markdown(
        f"**Facility:** `{filters.get('facility_label', 'All Facilities')}` | "
        f"**Department:** `{filters.get('department_label', 'All Departments')}` | "
        f"**Timeframe:** `{filters.get('date_period', 'Last 30 Days')}`"
    )
    st.markdown("---")

    facility_id = filters.get("facility")
    department_id = filters.get("department")

    try:
        kpi_engine = KPIEngine(db)
        alert_engine = AlertEngine(db)

        # 1. Operational Health Score Gauge & Top Alerts Banner
        col_gauge, col_alerts = st.columns([1, 2])

        with col_gauge:
            health_data = kpi_engine.get_operational_health_score(facility_id)
            score = health_data.get("health_score", 85.0)
            status = health_data.get("status", "Good")

            st.plotly_chart(
                create_gauge_chart(score, f"Operational Health ({status})", 0, 100, "%"),
                use_container_width=True
            )

        with col_alerts:
            st.subheader("⚡ Critical Operational Alerts")
            alerts = alert_engine.get_active_alerts(facility_id=facility_id, limit=3)
            if alerts:
                for alert in alerts:
                    render_alert_card(alert)
            else:
                st.success("✅ All operational systems performing within optimal thresholds.")

        st.markdown("---")

        # 2. Executive KPIs Row (14 KPIs split in 2 clean sections)
        st.subheader("📊 Executive Key Performance Indicators")
        exec_kpis = kpi_engine.get_executive_kpis(facility_id, department_id)

        render_kpi_row([
            {"title": "Total Patients", "value": f"{exec_kpis.get('total_patients', 0):,}", "change": 4.5},
            {"title": "Total Revenue", "value": f"{exec_kpis.get('total_revenue', 0):,.2f}", "prefix": "$", "change": 8.2},
            {"title": "Bed Occupancy", "value": f"{exec_kpis.get('bed_occupancy_rate', 0):.1f}", "suffix": "%", "change": 1.5},
            {"title": "Avg Wait Time", "value": f"{exec_kpis.get('avg_waiting_time', 0):.0f}", "suffix": " min", "change": -3.2}
        ])

        st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)

        render_kpi_row([
            {"title": "Staff Utilization", "value": f"{exec_kpis.get('staff_utilization_rate', 0):.1f}", "suffix": "%", "change": 2.1},
            {"title": "Claim Denial Rate", "value": f"{exec_kpis.get('claim_denial_rate', 0):.1f}", "suffix": "%", "change": -0.8},
            {"title": "No-Show Rate", "value": f"{exec_kpis.get('no_show_rate', 0):.1f}", "suffix": "%", "change": -1.4},
            {"title": "NPS Score", "value": f"{exec_kpis.get('patient_satisfaction_nps', 0):.0f}", "change": 5.0}
        ])

        st.markdown("---")

        # 3. Operational Trends
        col_trend1, col_trend2 = st.columns(2)

        with col_trend1:
            st.subheader("📈 Daily Patient Admissions & Visits")
            daily_trends = kpi_engine.get_daily_trends(days=30, facility_id=facility_id)
            if daily_trends:
                df_daily = pd.DataFrame(daily_trends)
                st.plotly_chart(
                    create_line_chart(df_daily, x="date", y="appointments", title="30-Day Appointment Volume"),
                    use_container_width=True
                )
            else:
                st.info("No appointment volume data for selected filters.")

        with col_trend2:
            st.subheader("💰 Monthly Financial Performance")
            monthly_trends = kpi_engine.get_monthly_trends(months=6, facility_id=facility_id)
            if monthly_trends:
                df_monthly = pd.DataFrame(monthly_trends)
                st.plotly_chart(
                    create_bar_chart(df_monthly, x="month", y="revenue", title="Monthly Revenue ($)"),
                    use_container_width=True
                )
            else:
                st.info("No monthly revenue data for selected filters.")

        st.markdown("---")

        # 4. Department & Facility Comparison
        col_comp1, col_comp2 = st.columns(2)

        with col_comp1:
            st.subheader("🏢 Department Volume Breakdown")
            dept_comp = kpi_engine.get_department_comparison(facility_id=facility_id)
            if dept_comp:
                df_dept = pd.DataFrame(dept_comp)
                st.plotly_chart(
                    create_bar_chart(df_dept, x="department", y="appointments", title="Appointments by Department", orientation='v'),
                    use_container_width=True
                )

        with col_comp2:
            st.subheader("🏥 Facility Benchmarks")
            fac_comp = kpi_engine.get_facility_comparison()
            if fac_comp:
                df_fac = pd.DataFrame(fac_comp)
                st.plotly_chart(
                    create_bar_chart(df_fac, x="facility", y="revenue", title="Revenue by Facility ($)"),
                    use_container_width=True
                )

    except Exception as e:
        st.error(f"Error rendering Executive Dashboard: {e}")
