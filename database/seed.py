import logging
from database.connection import get_db
from data.generators import SyntheticDataGenerator

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def chunk_list(data_list, chunk_size):
    """Yield successive chunk_size chunks from data_list."""
    for i in range(0, len(data_list), chunk_size):
        yield data_list[i:i + chunk_size]

def seed_database(batch_size=1000, force_reset=False):
    """
    Generates synthetic data and bulk inserts into MongoDB collections.
    
    SAFETY PRINCIPLE:
    Never deletes existing collections or records automatically.
    Seeds only missing data unless force_reset=True is explicitly passed.
    """
    db = get_db()
    if db is None:
        logger.error("Failed to connect to the database.")
        return

    logger.info("Initializing SyntheticDataGenerator...")
    generator = SyntheticDataGenerator()
    
    # Check if any collection needs data
    all_collections = [
        "patients", "staff", "appointments", "admissions", "billing",
        "insurance_claims", "medical_coding", "pharmacy_inventory",
        "laboratory_tests", "emergency_cases", "quality_incidents",
        "patient_feedback", "vendors", "purchase_orders", "financial_transactions"
    ]
    
    missing_collections = []
    for col_name in all_collections:
        count = db[col_name].count_documents({})
        if count == 0 or force_reset:
            missing_collections.append(col_name)
        else:
            logger.info(f"ℹ️ Collection '{col_name}' already contains {count} records. Skipping seed.")

    if not missing_collections:
        logger.info("✅ All collections already seeded. No missing data detected.")
        return

    logger.info(f"Generating synthetic data for collections: {missing_collections}...")
    data = generator.generate_all()

    for collection_name in missing_collections:
        records = data.get(collection_name, [])
        if not records:
            continue
            
        collection = db[collection_name]
        existing_count = collection.count_documents({})

        if existing_count > 0 and force_reset:
            logger.warning(f"⚠️ FORCE RESET requested. Clearing {existing_count} records from '{collection_name}'...")
            collection.delete_many({})

        logger.info(f"Seeding collection: '{collection_name}' with {len(records)} records...")
        total_inserted = 0
        for chunk in chunk_list(records, batch_size):
            try:
                result = collection.insert_many(chunk)
                total_inserted += len(result.inserted_ids)
            except Exception as e:
                logger.error(f"Error inserting batch into {collection_name}: {str(e)}")

        logger.info(f"  ✅ Inserted {total_inserted}/{len(records)} records into '{collection_name}'")
                
    logger.info("Database seeding completed successfully.")

if __name__ == "__main__":
    import sys
    force = "--force" in sys.argv
    seed_database(force_reset=force)
