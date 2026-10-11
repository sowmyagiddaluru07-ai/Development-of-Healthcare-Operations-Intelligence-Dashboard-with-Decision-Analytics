"""Pharmacy Management Page for Medical Operations Intelligence."""
import streamlit as st
import pandas as pd
from dashboard.components import (
    render_kpi_row,
    create_bar_chart,
    create_pie_chart
)
from analytics.operational_analytics import OperationalAnalytics


def render_pharmacy(db, filters):
    st.title("💊 Pharmacy Operations & Inventory Intelligence")
    facility_id = filters.get("facility")

    try:
        analytics = OperationalAnalytics(db)

        # 1. Pharmacy KPIs
        st.subheader("📦 Inventory Overview")
        pharm = analytics.get_pharmacy_status(facility_id)

        render_kpi_row([
            {"title": "Total SKU Items", "value": f"{pharm.get('total_items', 0):,}"},
            {"title": "Total Stock Value", "value": f"{pharm.get('total_value', 0):,.2f}", "prefix": "$"},
            {"title": "Low Stock Alerts", "value": f"{pharm.get('low_stock_count', 0):,}", "change": -2.0},
            {"title": "Expired Items", "value": f"{pharm.get('expired_count', 0):,}"}
        ])

        st.markdown("---")

        # 2. Stock Levels & Category Breakdown
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("🚨 Critical Low Stock Items")
            low_stock_items = pharm.get("low_stock_items", [])
            
            if low_stock_items:
                df_low = pd.DataFrame(low_stock_items)
                st.write("Available inventory columns:", df_low.columns.tolist())
                st.dataframe(df_low, use_container_width=True)
            else:
                st.success("✅ Stock levels adequate for all key medications.")

        with col2:
            st.subheader("🏷️ Stock Value by Category")
            by_cat = pharm.get("by_category", [])
            if by_cat:
                df_cat = pd.DataFrame(by_cat)
                
                st.plotly_chart(
                    create_bar_chart(
                        df_cat,
                        x="category",
                        y="total_stock",
                        title="Total Stock by Category",
                    ),
                    use_container_width=True,
                )

            else:
                st.info("No category data available.")

        st.markdown("---")

        
        # 3. Supply Chain & Purchase Orders Overview
        st.subheader("🚚 Supply Chain & Vendor Performance")
        vendors = analytics.get_vendor_analytics()

        if vendors:
            vendor_summary = {
                "Metric": [
                    "Total Vendors",
                    "Active Vendors",
                    "Average Rating",
                    "Average Reliability",
                ],
                "Value": [
                    vendors.get("total", 0),
                    vendors.get("active", 0),
                    vendors.get("avg_rating", 0),
                    vendors.get("avg_reliability", 0),
                ],
            }
            st.dataframe(
                pd.DataFrame(vendor_summary),
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info("No vendor data available.")


    except Exception as e:
        st.error(f"Error loading Pharmacy page: {e}")
