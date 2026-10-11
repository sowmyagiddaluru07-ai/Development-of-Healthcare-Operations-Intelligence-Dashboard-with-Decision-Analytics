"""
Database initialization - creates collections and indexes.
"""

from pymongo import ASCENDING, DESCENDING
from database.connection import get_db
from config.settings import Settings


def create_indexes(db):
    """Create all required indexes for optimal query performance."""
    indexes = {
        "patients": [
            [("patient_id", ASCENDING)],
            [("facility_id", ASCENDING)],
            [("registration_date", DESCENDING)],
            [("demographics.age_group", ASCENDING)],
        ],
        "appointments": [
            [("appointment_id", ASCENDING)],
            [("patient_id", ASCENDING)],
            [("doctor_id", ASCENDING)],
            [("facility_id", ASCENDING)],
            [("department_id", ASCENDING)],
            [("appointment_date", DESCENDING)],
            [("status", ASCENDING)],
            [("status", ASCENDING), ("appointment_date", DESCENDING)],
        ],
        "admissions": [
            [("admission_id", ASCENDING)],
            [("patient_id", ASCENDING)],
            [("facility_id", ASCENDING)],
            [("department_id", ASCENDING)],
            [("admission_date", DESCENDING)],
            [("status", ASCENDING)],
            [("bed_number", ASCENDING), ("facility_id", ASCENDING)],
        ],
        "staff": [
            [("staff_id", ASCENDING)],
            [("facility_id", ASCENDING)],
            [("department_id", ASCENDING)],
            [("role", ASCENDING)],
            [("status", ASCENDING)],
        ],
        "billing": [
            [("bill_id", ASCENDING)],
            [("patient_id", ASCENDING)],
            [("facility_id", ASCENDING)],
            [("department_id", ASCENDING)],
            [("bill_date", DESCENDING)],
            [("payment_status", ASCENDING)],
        ],
        "insurance_claims": [
            [("claim_id", ASCENDING)],
            [("patient_id", ASCENDING)],
            [("status", ASCENDING)],
            [("submission_date", DESCENDING)],
            [("payer", ASCENDING)],
        ],
        "medical_coding": [
            [("coding_id", ASCENDING)],
            [("bill_id", ASCENDING)],
            [("status", ASCENDING)],
        ],
        "pharmacy_inventory": [
            [("medicine_id", ASCENDING)],
            [("facility_id", ASCENDING)],
            [("category", ASCENDING)],
            [("stock_quantity", ASCENDING)],
            [("expiry_date", ASCENDING)],
        ],
        "laboratory_tests": [
            [("test_id", ASCENDING)],
            [("patient_id", ASCENDING)],
            [("facility_id", ASCENDING)],
            [("department_id", ASCENDING)],
            [("test_date", DESCENDING)],
            [("status", ASCENDING)],
        ],
        "emergency_cases": [
            [("case_id", ASCENDING)],
            [("patient_id", ASCENDING)],
            [("facility_id", ASCENDING)],
            [("arrival_time", DESCENDING)],
            [("triage_level", ASCENDING)],
        ],
        "quality_incidents": [
            [("incident_id", ASCENDING)],
            [("facility_id", ASCENDING)],
            [("severity", ASCENDING)],
            [("status", ASCENDING)],
            [("reported_date", DESCENDING)],
        ],
        "patient_feedback": [
            [("feedback_id", ASCENDING)],
            [("patient_id", ASCENDING)],
            [("facility_id", ASCENDING)],
            [("department_id", ASCENDING)],
            [("feedback_date", DESCENDING)],
            [("rating", ASCENDING)],
        ],
        "vendors": [
            [("vendor_id", ASCENDING)],
            [("category", ASCENDING)],
            [("status", ASCENDING)],
        ],
        "purchase_orders": [
            [("po_id", ASCENDING)],
            [("vendor_id", ASCENDING)],
            [("facility_id", ASCENDING)],
            [("order_date", DESCENDING)],
            [("status", ASCENDING)],
        ],
        "financial_transactions": [
            [("transaction_id", ASCENDING)],
            [("facility_id", ASCENDING)],
            [("department_id", ASCENDING)],
            [("transaction_date", DESCENDING)],
            [("type", ASCENDING)],
            [("category", ASCENDING)],
        ],
        "operational_alerts": [
            [("alert_id", ASCENDING)],
            [("facility_id", ASCENDING)],
            [("alert_type", ASCENDING)],
            [("severity", ASCENDING)],
            [("status", ASCENDING)],
            [("created_at", DESCENDING)],
        ],
        "audit_logs": [
            [("log_id", ASCENDING)],
            [("action", ASCENDING)],
            [("timestamp", DESCENDING)],
            [("user_role", ASCENDING)],
        ],
    }

    for collection_name, idx_list in indexes.items():
        col = db[collection_name]
        for idx_keys in idx_list:
            try:
                col.create_index(idx_keys, background=True)
            except Exception as e:
                print(f"  ⚠️ Index warning on {collection_name}: {e}")

    print(f"  ✅ Created indexes for {len(indexes)} collections")


def initialize_database():
    """Initialize MongoDB database with collections and indexes."""
    print("\n📦 Initializing database...")
    db = get_db()

    # Create collections if they don't exist
    existing = set(db.list_collection_names())
    for col_name in Settings.COLLECTIONS:
        if col_name not in existing:
            db.create_collection(col_name)
            print(f"  ✅ Created collection: {col_name}")
        else:
            print(f"  ℹ️ Collection exists: {col_name}")

    # Create indexes
    print("\n📑 Creating indexes...")
    create_indexes(db)

    print("\n✅ Database initialization complete.")
    return True


def check_data_exists(db):
    """Check if data has already been seeded."""
    patients_count = db["patients"].count_documents({})
    return patients_count > 0


def get_collection_stats(db):
    """Get document counts for all collections."""
    stats = {}
    for col_name in Settings.COLLECTIONS:
        stats[col_name] = db[col_name].count_documents({})
    return stats
