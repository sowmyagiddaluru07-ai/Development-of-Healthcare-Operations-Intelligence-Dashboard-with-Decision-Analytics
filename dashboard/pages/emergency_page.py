"""Emergency Department Operations Page for Medical Operations Intelligence."""
import streamlit as st
import pandas as pd
from dashboard.components import (
    render_kpi_row,
    create_bar_chart,
    create_pie_chart
)
from analytics.operational_analytics import OperationalAnalytics


def render_emergency(db, filters):
    st.title("🚨 Emergency Department Intelligence")
    facility_id = filters.get("facility")

    try:
        analytics = OperationalAnalytics(db)

        # 1. ER KPIs
        st.subheader("⚡ Real-Time ER Metrics")
        er = analytics.get_emergency_analytics(facility_id)

        render_kpi_row([
            {"title": "Total ER Cases", "value": f"{er.get('total_cases', 0):,}"},
            {"title": "Avg Triage-to-Doctor", "value": f"{er.get('avg_waiting_time', 0):.0f}", "suffix": " min"},
            {"title": "Critical Cases (L1/L2)", "value": f"{er.get('critical_cases', 0):,}"},
            {"title": "Admission Rate", "value": f"{er.get('admission_rate', 0):.1f}", "suffix": "%"}
        ])

        st.markdown("---")

        # 2. Triage Level Breakdown & Waiting Times
        col1, col2 = st.columns(2)

        
        with col1:
            st.subheader("🎯 Cases by Triage Severity Level")
            by_triage = er.get("by_triage", [])

            if by_triage:
                df_triage = pd.DataFrame(by_triage)
                st.plotly_chart(
                    create_bar_chart(
                        df_triage,
                        x="level",
                        y="count",
                        title="Cases by Triage Severity Level",
                    ),
                    use_container_width=True,
                )
            else:
                st.info("No triage case data available.")

        
        with col2:
            st.subheader("⏱️ Avg Wait Time by Triage Level")
            if by_triage:
                df_triage = pd.DataFrame(by_triage)
                st.plotly_chart(
                    create_bar_chart(
                        df_triage,
                        x="level",
                        y="avg_wait",
                        title="Average Wait Time by Triage Level",
                    ),
                    use_container_width=True,
                )
            else:
                st.info("No triage wait-time data available.")


    except Exception as e:
        st.error(f"Error loading Emergency Department page: {e}")
