
"""Patient Operations Page for Medical Operations Intelligence."""

import streamlit as st
import pandas as pd

from dashboard.components import (
    render_kpi_row,
    create_line_chart,
    create_bar_chart,
    create_pie_chart,
)

from analytics.patient_analytics import PatientAnalytics


def render_patient_operations(db, filters):
    st.title("👤 Patient Operations & Flow Intelligence")

    facility_id = filters.get("facility")
    department_id = filters.get("department")

    try:
        analytics = PatientAnalytics(db)

        # 1. Patient Flow Overview
        st.subheader("📌 Patient Flow Overview")

        flow_data = analytics.get_patient_flow(facility_id, days=30)
        if not isinstance(flow_data, list):
            flow_data = []

        total_registrations = sum(
            row.get("registrations", 0) for row in flow_data
        )
        total_admissions = sum(
            row.get("admissions", 0) for row in flow_data
        )
        total_discharges = sum(
            row.get("discharges", 0) for row in flow_data
        )

        render_kpi_row([
            {
                "title": "Registrations (Last 30 Days)",
                "value": f"{total_registrations:,}",
            },
            {
                "title": "Admissions (Last 30 Days)",
                "value": f"{total_admissions:,}",
            },
            {
                "title": "Discharges (Last 30 Days)",
                "value": f"{total_discharges:,}",
            },
            {
                "title": "Days with Activity",
                "value": f"{len(flow_data):,}",
            },
        ])

        st.markdown("---")

        # 2. Appointment Analytics and Waiting Time
        col_appt1, col_appt2 = st.columns(2)

        with col_appt1:
            st.subheader("📅 Appointment Status Breakdown")

            appt_data = analytics.get_appointment_analytics(
                facility_id, department_id
            )

            status_dist = (
                appt_data.get("status_distribution", [])
                if isinstance(appt_data, dict)
                else []
            )

            if status_dist:
                df_status = pd.DataFrame(status_dist)

                if {"status", "count"}.issubset(df_status.columns):
                    st.plotly_chart(
                        create_pie_chart(
                            df_status,
                            names="status",
                            values="count",
                            title="Appointment Status Distribution",
                        ),
                        use_container_width=True,
                    )
                else:
                    st.warning(
                        "Appointment status data is missing the "
                        "'status' or 'count' column."
                    )
            else:
                st.info("No appointment distribution data.")

        with col_appt2:
            st.subheader("⏱️ Waiting Time by Department")

            wait_data = analytics.get_waiting_time_analysis(facility_id)

            if isinstance(wait_data, list) and wait_data:
                df_wait = pd.DataFrame(wait_data)

                if {"department", "avg_wait"}.issubset(df_wait.columns):
                    st.plotly_chart(
                        create_bar_chart(
                            df_wait,
                            x="department",
                            y="avg_wait",
                            title="Avg Wait Time (Minutes)",
                        ),
                        use_container_width=True,
                    )
                else:
                    st.warning(
                        "Waiting-time data is missing the expected columns."
                    )
            else:
                st.info("No waiting time data available.")

        st.markdown("---")

        # 3. Admissions and Readmission Analysis
        col_adm1, col_adm2 = st.columns(2)

        with col_adm1:
            st.subheader("🏥 Length of Stay Distribution")

            adm_data = analytics.get_admission_analytics(facility_id)

            los_dist = (
                adm_data.get("los_distribution", [])
                if isinstance(adm_data, dict)
                else []
            )

            if los_dist:
                df_los = pd.DataFrame(los_dist)

                if {"range", "count"}.issubset(df_los.columns):
                    st.plotly_chart(
                        create_bar_chart(
                            df_los,
                            x="range",
                            y="count",
                            title="Admissions by Length of Stay",
                        ),
                        use_container_width=True,
                    )
                else:
                    st.info(
                        "Length-of-stay data has a different structure "
                        "than expected."
                    )
            else:
                st.info("No length-of-stay data available.")

            if isinstance(adm_data, dict):
                st.metric(
                    "Total Admissions",
                    f"{adm_data.get('total_admissions', 0):,}",
                )
                st.metric(
                    "Currently Admitted",
                    f"{adm_data.get('currently_admitted', 0):,}",
                )

        with col_adm2:
            st.subheader("🚫 No-Show Analysis")

            ns_data = analytics.get_no_show_analysis(facility_id)

            by_dept_ns = (
                ns_data.get("by_department", [])
                if isinstance(ns_data, dict)
                else []
            )

            if by_dept_ns:
                df_ns = pd.DataFrame(by_dept_ns)

                if {"department", "rate"}.issubset(df_ns.columns):
                    st.plotly_chart(
                        create_bar_chart(
                            df_ns,
                            x="department",
                            y="rate",
                            title="No-Show Rate (%) by Department",
                        ),
                        use_container_width=True,
                    )
                else:
                    st.warning(
                        "No-show data is missing the expected columns."
                    )
            else:
                st.info("No no-show data available.")

        st.markdown("---")

        # 4. Patient Demographics
        st.subheader("👥 Patient Demographics Distribution")

        demo_data = analytics.get_patient_demographics(facility_id)

        if not isinstance(demo_data, dict):
            demo_data = {}

        age_dist = demo_data.get("age_groups", [])
        gender_dist = demo_data.get("gender", [])

        col_demo1, col_demo2 = st.columns(2)

        with col_demo1:
            st.subheader("Age Group Breakdown")

            if age_dist:
                df_age = pd.DataFrame(age_dist)

                if {"age_group", "count"}.issubset(df_age.columns):
                    st.plotly_chart(
                        create_bar_chart(
                            df_age,
                            x="age_group",
                            y="count",
                            title="Age Group Breakdown",
                        ),
                        use_container_width=True,
                    )
                else:
                    st.info("Age-group data has an unexpected structure.")
            else:
                st.info("No age demographic data available.")

        with col_demo2:
            st.subheader("Gender Distribution")

            if gender_dist:
                df_gender = pd.DataFrame(gender_dist)

                if {"gender", "count"}.issubset(df_gender.columns):
                    st.plotly_chart(
                        create_pie_chart(
                            df_gender,
                            names="gender",
                            values="count",
                            title="Gender Distribution",
                        ),
                        use_container_width=True,
                    )
                else:
                    st.info("Gender data has an unexpected structure.")
            else:
                st.info("No gender demographic data available.")

    except Exception as e:
        st.error(f"Error loading Patient Operations: {e}")
        st.exception(e)
