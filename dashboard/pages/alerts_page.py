"""Operational Alerts Page for Medical Operations Intelligence."""
import streamlit as st
import pandas as pd
from dashboard.components import (
    render_kpi_row,
    render_alert_card
)
from automation.alert_engine import AlertEngine


def render_alerts(db, filters):
    st.title("🚨 Operational Alert Center & Rules Automation")
    facility_id = filters.get("facility")

    try:
        alert_engine = AlertEngine(db)

        # 1. Action to execute automated rules check
        col_title, col_btn = st.columns([3, 1])
        with col_btn:
            if st.button("⚡ Run Rule Detection Engine"):
                with st.spinner("Evaluating capacity, wait times, inventory & financial rules..."):
                    summary = alert_engine.run_all_checks()
                    st.success(f"Checks completed. New alerts generated: {summary.get('new_alerts', 0)}")

        st.markdown("---")

        # 2. Active Alert Summary Metrics
        summary = alert_engine.get_alert_summary(facility_id)

        render_kpi_row([
            {"title": "Total Active Alerts", "value": f"{summary.get('total_active', 0):,}"},
            {"title": "Critical Severity", "value": f"{summary.get('by_severity', {}).get('CRITICAL', 0):,}"},
            {"title": "High Severity", "value": f"{summary.get('by_severity', {}).get('HIGH', 0):,}"},
            {"title": "Medium/Low Severity", "value": f"{summary.get('by_severity', {}).get('MEDIUM', 0) + summary.get('by_severity', {}).get('LOW', 0):,}"}
        ])

        st.markdown("---")

        # 3. Active Alert List with Actions
        st.subheader("📋 Active Operational Alerts")
        active_alerts = alert_engine.get_active_alerts(facility_id=facility_id, limit=20)

        if active_alerts:
            for alert in active_alerts:
                col_card, col_action = st.columns([4, 1])
                with col_card:
                    render_alert_card(alert)
                with col_action:
                    alert_id = alert.get("alert_id")
                    if st.button(f"Resolve", key=f"res_{alert_id}"):
                        alert_engine.resolve_alert(alert_id)
                        st.success(f"Alert {alert_id} resolved!")
                        st.rerun()
        else:
            st.success("🎉 No active operational alerts for the selected facility.")

    except Exception as e:
        st.error(f"Error loading Operational Alerts: {e}")
