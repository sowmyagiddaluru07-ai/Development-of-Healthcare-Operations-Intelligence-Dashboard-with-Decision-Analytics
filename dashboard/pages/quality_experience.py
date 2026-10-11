"""Quality & Patient Experience Page for Medical Operations Intelligence."""
import streamlit as st
import pandas as pd
from dashboard.components import (
    render_kpi_row,
    create_bar_chart,
    create_pie_chart
)
from analytics.operational_analytics import OperationalAnalytics


def render_quality_experience(db, filters):
    st.title("⭐ Quality, Incident & Patient Experience")
    facility_id = filters.get("facility")

    try:
        analytics = OperationalAnalytics(db)

        # 1. Quality & Satisfaction KPIs
        st.subheader("🌟 Quality Scorecard")
        feedback = analytics.get_feedback_analytics(facility_id)
        quality = analytics.get_quality_metrics(facility_id)

        render_kpi_row([
            {"title": "Avg Patient Rating", "value": f"{feedback.get('avg_rating', 0):.2f}", "suffix": " / 5.0"},
            {"title": "Patient NPS", "value": f"{feedback.get('nps_score', 0):.0f}"},
            {"title": "Total Quality Incidents", "value": f"{quality.get('total_incidents', 0):,}"},
            {"title": "High Severity Incidents", "value": f"{quality.get('high_severity_count', 0):,}"}
        ])

        st.markdown("---")

        # 2. Sentiment Analysis & Incident Severity
        col1, col2 = st.columns(2)

        
        with col1:
            st.subheader("💬 Patient Sentiment Distribution")
            sentiment = feedback.get("sentiment_distribution", [])

            if sentiment:
                df_sent = pd.DataFrame(sentiment)
                st.plotly_chart(
                    create_pie_chart(
                        df_sent,
                        names="sentiment",
                        values="count",
                        title="Feedback Sentiment Share",
                    ),
                    use_container_width=True,
                )
            else:
                st.info("No patient sentiment data available.")


        
        with col2:
            st.subheader("⚠️ Incidents by Severity Level")
            by_sev = quality.get("by_severity", [])

            if by_sev:
                df_sev = pd.DataFrame(by_sev)
                st.plotly_chart(
                    create_bar_chart(
                        df_sev,
                        x="severity",
                        y="count",
                        title="Quality Incidents Severity",
                    ),
                    use_container_width=True,
                )
            else:
                st.info("No quality incident data available.")

    except Exception as e:
        st.error(f"Error loading Quality & Experience page: {e}")
