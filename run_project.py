"""Master project runner - initializes and launches everything."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    print('='*60)
    print('Medical Operations Intelligence Dashboard')
    print('='*60)
    
    # Step 1: Check environment
    print('\n[1/10] Checking environment...')
    from dotenv import load_dotenv
    load_dotenv()
    
    from config.settings import Settings
    errors = Settings.validate()
    if errors:
        for e in errors:
            print(f'  ERROR: {e}')
        print('\nPlease configure .env file. See .env.example')
        sys.exit(1)
    print('  OK Environment configured')
    
    # Step 2: Test MongoDB
    print('\n[2/10] Connecting to MongoDB...')
    try:
        from database.connection import get_db, db_connection
        db = get_db()
    except Exception as e:
        print(f'  FAILED: {e}')
        sys.exit(1)
    
    # Step 3: Initialize database
    print('\n[3/10] Initializing database...')
    from database.initialization import initialize_database
    initialize_database()
    
    # Step 4: Seed data
    print('\n[4/10] Checking/seeding data...')
    from database.seed import seed_database
    seed_database()
    
    # Step 5: Run analytics (quick validation)
    print('\n[5/10] Validating analytics...')
    try:
        from analytics.kpi_engine import KPIEngine
        kpi = KPIEngine(db)
        kpis = kpi.get_executive_kpis()
        print(f'  Total patients: {kpis.get("total_patients", 0):,}')
        print(f'  Total appointments: {kpis.get("total_appointments", 0):,}')
        print(f'  Health Score: {kpis.get("operational_health_score", 0):.1f}/100')
    except Exception as e:
        print(f'  Analytics warning: {e}')
    
    # Step 6: Train ML models
    print('\n[6/10] Training ML models...')
    try:
        from ml.model_manager import ModelManager
        mm = ModelManager(db)
        results = mm.train_all_models()
        for model, status in results.items():
            print(f'  {model}: {status}')
    except Exception as e:
        print(f'  ML warning: {e}')
    
    # Step 7: Run automation
    print('\n[7/10] Running automation rules...')
    try:
        from automation.alert_engine import AlertEngine
        ae = AlertEngine(db)
        alert_summary = ae.run_all_checks()
        print(f'  Alerts generated: {alert_summary.get("total_alerts", 0)}')
    except Exception as e:
        print(f'  Automation warning: {e}')
    
    # Step 8: Generate Power BI exports
    print('\n[8/10] Generating Power BI exports...')
    try:
        from powerbi.export_engine import PowerBIExporter
        exporter = PowerBIExporter(db)
        export_summary = exporter.export_all()
        print(f'  Files exported: {export_summary.get("total_files", 0)}')
    except Exception as e:
        print(f'  Export warning: {e}')
    
    # Step 9: Log audit
    print('\n[9/10] Logging initialization...')
    try:
        from automation.audit_logger import AuditLogger
        logger = AuditLogger(db)
        logger.log('SYSTEM_INITIALIZATION', 'System', 'Full project initialization completed')
    except Exception as e:
        print(f'  Audit warning: {e}')
    
    # Step 10: Launch dashboard
    print('\n[10/10] Launching Streamlit Dashboard...')
    print('='*60)
    print('Dashboard URL: http://localhost:8501')
    print('Press Ctrl+C to stop')
    print('='*60)
    
    os.system(f'{sys.executable} -m streamlit run app.py --server.port=8501 --server.headless=true')

if __name__ == '__main__':
    main()
