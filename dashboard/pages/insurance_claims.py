"""Insurance Claims Page for Medical Operations Intelligence."""
import streamlit as st
import pandas as pd
from dashboard.components import (
    render_kpi_row,
    create_bar_chart,
    create_pie_chart,
    create_line_chart
)
from analytics.claims_analytics import ClaimsAnalytics


def render_insurance_claims(db, filters):
    st.title("🛡️ Insurance Claims & Denial Management")
    facility_id = filters.get("facility")

    try:
        analytics = ClaimsAnalytics(db)

        # 1. Claims Overview KPIs
        st.subheader("📑 Claims Summary")
        overview = analytics.get_claims_overview(facility_id)

        render_kpi_row([
            {"title": "Total Claims Submitted", "value": f"{overview.get('total_claims', 0):,}"},
            {"title": "Total Amount Claimed", "value": f"{overview.get('total_claimed', 0):,.2f}", "prefix": "$"},
            {"title": "Claim Denial Rate", "value": f"{overview.get('denial_rate', 0):.1f}", "suffix": "%"},
            {"title": "Avg Processing Days", "value": f"{overview.get('avg_processing_days', 0):.1f}", "suffix": " days"}
        ])

        st.markdown("---")

        # 2. Denial Reason Breakdown & Payer Performance
        col1, col2 = st.columns(2)

        
        
        with col1:
            st.subheader("❌ Top Denial Reasons")
            denials = analytics.get_denial_analysis(facility_id)

            st.write("Denial data returned:")
            st.write(denials)

            if isinstance(denials, list) and denials:
                df_reason = pd.DataFrame(denials)
                st.write("Denial data columns:", df_reason.columns.tolist())
                st.dataframe(df_reason, use_container_width=True)
            else:
                st.info("No claim denial data available.")


        with col2:
            st.subheader("🏢 Payer Denial Rate Comparison")
            payers = analytics.get_payer_comparison(facility_id)
            if payers:
                df_payer = pd.DataFrame(payers)
                st.plotly_chart(
                    create_bar_chart(df_payer, x="payer", y="denial_rate", title="Denial Rate (%) by Payer"),
                    use_container_width=True
                )
            else:
                st.info("No payer comparison data.")

        st.markdown("---")

        
        # 3. Claim Aging & Monthly Submission Trend
        col3, col4 = st.columns(2)

        with col3:
            st.subheader("⏳ Claim Aging Breakdown")
            aging = analytics.get_claim_aging(facility_id)

            if aging:
                df_aging = pd.DataFrame(aging)
                st.dataframe(df_aging, use_container_width=True)
            else:
                st.info("No claim aging data available.")

        with col4:
            st.subheader("📅 Monthly Claim Submission Trend")
            st.info("Monthly submission trend will be added after checking the analytics data.")


    except Exception as e:
        st.error(f"Error loading Insurance Claims page: {e}")
