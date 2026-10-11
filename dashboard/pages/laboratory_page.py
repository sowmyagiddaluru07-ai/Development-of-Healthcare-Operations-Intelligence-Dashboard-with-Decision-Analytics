"""Laboratory Intelligence Page for Medical Operations Intelligence."""
import streamlit as st
import pandas as pd
from dashboard.components import (
    render_kpi_row,
    create_bar_chart,
    create_pie_chart
)
from analytics.operational_analytics import OperationalAnalytics


def render_laboratory(db, filters):
    st.title("🔬 Laboratory Operations & SLA Tracking")
    facility_id = filters.get("facility")

    try:
        analytics = OperationalAnalytics(db)

        # 1. Lab KPIs
        st.subheader("📊 Test Summary & SLA Compliance")
        lab = analytics.get_lab_analytics(facility_id)

        render_kpi_row([
            {"title": "Total Lab Tests", "value": f"{lab.get('total_tests', 0):,}"},
            {"title": "Avg Turnaround Time", "value": f"{lab.get('avg_turnaround_time', 0):.0f}", "suffix": " min"},
            {"title": "Abnormal Results", "value": f"{lab.get('abnormal_count', 0):,}"},
            {"title": "Completed Tests", "value": f"{lab.get('completed_count', 0):,}"}
        ])

        st.markdown("---")

        # 2. Test Volume & Turnaround Time by Category
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("🧪 Test Volume by Category")
            by_type = lab.get("by_type", [])
            if by_type:
                df_type = pd.DataFrame(by_type)
                st.plotly_chart(
                    create_bar_chart(df_type, x="_id", y="count", title="Total Tests Processed"),
                    use_container_width=True
                )
            else:
                st.info("No test category data.")

        with col2:
            st.subheader("⏱️ Avg Turnaround Time by Category")
            if by_type:
                df_type = pd.DataFrame(by_type)
                st.plotly_chart(
                    create_bar_chart(df_type, x="_id", y="avg_tat", title="Turnaround Time (Minutes)"),
                    use_container_width=True
                )

    except Exception as e:
        st.error(f"Error loading Laboratory page: {e}")
