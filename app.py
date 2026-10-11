import streamlit as st

# Configure page
st.set_page_config(page_title="Medical Operations Intelligence", layout="wide", initial_sidebar_state="expanded")


# Inject custom CSS for dark theme
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .stApp {
        background: linear-gradient(135deg, #0b1120 0%, #111827 100%);
        color: #e5edf7;
    }

    [data-testid="stHeader"] {
        background: rgba(11, 17, 32, 0.95);
    }

    [data-testid="stSidebar"] {
        background: #151c2c;
        border-right: 1px solid #293950;
    }

    h1 {
        color: #f8fafc !important;
        font-weight: 700 !important;
        font-size: 2rem !important;
    }

    h2, h3 {
        color: #e2e8f0 !important;
        font-weight: 600 !important;
    }

    [data-testid="stMetric"] {
        background: #151f31;
        border: 1px solid #293950;
        border-radius: 12px;
        padding: 16px;
    }

    [data-testid="stAlert"] {
        border-radius: 10px;
    }

    hr {
        border-color: #293950;
    }

    .stButton button {
        border-radius: 8px;
        border: 1px solid #14b8a6;
    }
</style>
""", unsafe_allow_html=True)

# Imports for dashboard pages
from dashboard.components import apply_filters
from dashboard.pages.executive_dashboard import render_executive_dashboard
from dashboard.pages.patient_operations import render_patient_operations
from dashboard.pages.staff_intelligence import render_staff_intelligence
from dashboard.pages.revenue_intelligence import render_revenue_intelligence
from dashboard.pages.insurance_claims import render_insurance_claims
from dashboard.pages.pharmacy_page import render_pharmacy
from dashboard.pages.laboratory_page import render_laboratory
from dashboard.pages.emergency_page import render_emergency
from dashboard.pages.quality_experience import render_quality_experience
from dashboard.pages.ai_predictions import render_ai_predictions
from dashboard.pages.alerts_page import render_alerts
from dashboard.pages.copilot_page import render_copilot

from database.connection import get_db

def main():
    try:
        db = get_db()
    except Exception as e:
        st.error(f"Failed to connect to database: {e}")
        st.warning("Please verify your MONGODB_URI configuration in .env file.")
        return

    st.sidebar.title("MOI Dashboard")
    
    pages = {
        "Executive Dashboard": render_executive_dashboard,
        "Patient Operations": render_patient_operations,
        "Staff Intelligence": render_staff_intelligence,
        "Revenue Intelligence": render_revenue_intelligence,
        "Insurance Claims": render_insurance_claims,
        "Pharmacy": render_pharmacy,
        "Laboratory": render_laboratory,
        "Emergency": render_emergency,
        "Quality & Experience": render_quality_experience,
        "AI Predictions": render_ai_predictions,
        "Alerts": render_alerts,
        "Copilot": render_copilot
    }
    
    selection = st.sidebar.radio("Navigation", list(pages.keys()))
    
    # Apply filters
    filters = apply_filters()
    
    # Render selected page
    try:
        pages[selection](db, filters)
    except Exception as e:
        st.error(f"An error occurred while rendering the page: {e}")
        
    # Footer
    st.markdown("---")
    st.markdown("<p style='text-align: center; color: #a0a0a0;'>Medical Operations Intelligence © 2026</p>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
