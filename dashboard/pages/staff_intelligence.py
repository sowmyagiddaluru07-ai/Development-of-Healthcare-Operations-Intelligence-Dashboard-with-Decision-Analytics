"""Staff Intelligence Page for Medical Operations Intelligence."""
import streamlit as st
import pandas as pd
from dashboard.components import (
    render_kpi_row,
    create_bar_chart,
    create_pie_chart
)
from analytics.staff_analytics import StaffAnalytics



def render_staff_intelligence(db, filters):
    st.title("👨‍⚕️ Staff Intelligence & Workforce Analytics")
    facility_id = filters.get("facility")
    department_id = filters.get("department")

    try:
        analytics = StaffAnalytics(db)

        # 1. Staff Overview KPIs
        st.subheader("📋 Workforce Summary")
        overview = analytics.get_staff_overview(facility_id)

        render_kpi_row([
            {"title": "Total Staff", "value": f"{overview.get('total_staff', 0):,}"},
            {"title": "Active Doctors", "value": f"{overview.get('doctors_count', 0):,}"},
            {"title": "Active Nurses", "value": f"{overview.get('nurses_count', 0):,}"},
            {"title": "Avg Utilization", "value": f"{overview.get('avg_utilization', 0):.1f}", "suffix": "%"}
        ])

        st.markdown("---")

        
        # 2. Doctor Productivity & Workload
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("🩺 Doctor Productivity Scorecard")
            prod = analytics.get_doctor_productivity(facility_id)

            if prod:
                df_prod = pd.DataFrame(prod[:10])

                st.plotly_chart(
                    create_bar_chart(
                        df_prod,
                        x="name",
                        y="appointments",
                        title="Appointments Processed per Doctor",
                    ),
                    use_container_width=True,
                )
            else:
                st.info("No doctor productivity data available.")

        
        with col2:
            st.subheader("⚡ Staff Utilization by Role")

            util = analytics.get_staff_utilization(facility_id)

            by_role = (
                util
                if isinstance(util, list)
                else util.get("by_role", [])
                if isinstance(util, dict)
                else []
            )

            if by_role:
                df_role = pd.DataFrame(by_role)
                st.write("Available data columns:", df_role.columns.tolist())
                st.dataframe(df_role, use_container_width=True)
            else:
                st.info("No utilization data available.")


        st.markdown("---")

        # 3. Workload & Overtime Risk
        col3, col4 = st.columns(2)

        
        with col3:
            st.subheader("⏳ Department Workload Distribution")

            workload = analytics.get_workload_analysis(facility_id)
            by_dept = workload if isinstance(workload, list) else (
                workload.get("by_department", [])
                if isinstance(workload, dict)
                else []
            )

            if by_dept:
                df_workload = pd.DataFrame(by_dept)

                st.write("Available workload columns:", df_workload.columns.tolist())
                st.dataframe(df_workload, use_container_width=True)
            else:
                st.info("No department workload data available.")


        with col4:
            st.subheader("🚨 Overtime Alerts & Staff Burnout Risk")

            alerts = analytics.get_overtime_alerts(facility_id)

            if isinstance(alerts, list) and alerts:
                df_alerts = pd.DataFrame(alerts)

                expected_columns = [
                    "staff_id",
                    "name",
                    "role",
                    "overtime_hours",
                    "utilization_rate",
                ]
                available_columns = [
                    col for col in expected_columns
                    if col in df_alerts.columns
                ]

                if available_columns:
                    st.dataframe(
                        df_alerts[available_columns],
                        use_container_width=True,
                    )
                else:
                    st.dataframe(df_alerts, use_container_width=True)

            elif isinstance(alerts, dict):
                st.write(alerts)
            else:
                st.success("✅ No staff exceeding overtime limits.")

    except Exception as e:
        st.error(f"Error loading Staff Intelligence: {e}")
        st.exception(e)