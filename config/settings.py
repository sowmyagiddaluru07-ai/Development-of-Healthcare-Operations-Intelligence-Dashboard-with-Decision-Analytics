"""
Application settings and configuration.
Loads environment variables and provides centralized configuration.
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Settings:
    """Central application settings."""

    # Application
    APP_NAME = os.getenv("APP_NAME", "Medical Operations Intelligence")
    APP_ENV = os.getenv("APP_ENV", "development")
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"

    # MongoDB
    MONGODB_URI = os.getenv("MONGODB_URI", "")
    DATABASE_NAME = "medical_operations"

    # Facilities
    FACILITIES = [
        {"id": "FAC001", "name": "Central Hospital", "type": "Main", "beds": 500},
        {"id": "FAC002", "name": "City Care Hospital", "type": "Secondary", "beds": 300},
        {"id": "FAC003", "name": "North Branch", "type": "Branch", "beds": 150},
        {"id": "FAC004", "name": "South Branch", "type": "Branch", "beds": 150},
    ]

    # Departments
    DEPARTMENTS = [
        {"id": "DEP001", "name": "Emergency", "type": "Clinical"},
        {"id": "DEP002", "name": "Cardiology", "type": "Clinical"},
        {"id": "DEP003", "name": "Neurology", "type": "Clinical"},
        {"id": "DEP004", "name": "Orthopedics", "type": "Clinical"},
        {"id": "DEP005", "name": "Pediatrics", "type": "Clinical"},
        {"id": "DEP006", "name": "General Medicine", "type": "Clinical"},
        {"id": "DEP007", "name": "Surgery", "type": "Clinical"},
        {"id": "DEP008", "name": "ICU", "type": "Critical Care"},
        {"id": "DEP009", "name": "Dermatology", "type": "Clinical"},
        {"id": "DEP010", "name": "Gynecology", "type": "Clinical"},
    ]

    # Alert Thresholds
    BED_OCCUPANCY_THRESHOLD = 85  # percent
    WAITING_TIME_THRESHOLD = 45  # minutes
    CLAIM_AGING_THRESHOLD = 30  # days
    PHARMACY_EXPIRY_DAYS = 30  # days before expiry
    LAB_PENDING_THRESHOLD = 24  # hours
    STAFF_OVERTIME_THRESHOLD = 10  # hours per week
    PAYMENT_AGING_THRESHOLD = 60  # days
    STAFF_COVERAGE_MIN = 0.7  # 70% minimum

    # ML Settings
    FORECAST_DAYS = 30
    ANOMALY_CONTAMINATION = 0.05

    # Roles
    ROLES = ["Admin", "Hospital Manager", "Department Manager", "Operations Analyst"]

    # Collections
    COLLECTIONS = [
        "patients", "appointments", "admissions", "staff", "billing",
        "insurance_claims", "medical_coding", "pharmacy_inventory",
        "laboratory_tests", "emergency_cases", "quality_incidents",
        "patient_feedback", "vendors", "purchase_orders",
        "financial_transactions", "operational_alerts", "audit_logs",
    ]

    @classmethod
    def validate(cls):
        """Validate critical configuration."""
        errors = []
        if not cls.MONGODB_URI:
            errors.append("MONGODB_URI is not set. Please configure it in .env file.")
        return errors
