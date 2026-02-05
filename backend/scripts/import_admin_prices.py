"""
Script to import the standard price list for the admin user's company.
Run: docker compose exec backend python scripts/import_admin_prices.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import User, PriceItem
from scripts.import_prices_manual import import_all

def run_import():
    db = SessionLocal()
    try:
        # Find the admin user (prefer 'admin@example.com' or just any admin)
        admin = db.query(User).filter(User.is_admin == True).order_by(User.id.asc()).first()
        if not admin:
            print("Error: No admin user found. Create one first.")
            return
        
        if not admin.company:
            # Create company if missing
            from app.models import Company
            admin.company = Company(user_id=admin.id)
            db.add(admin.company)
            db.commit()
            db.refresh(admin)

        print(f"Found admin: {admin.email} (Company ID: {admin.company.id})")
        print("Starting price import (upsert mode)...")
        
        # We don't delete to avoid Foreign Key violations. 
        # import_all from scripts.import_prices_manual will skip if exists.
        # But we want to ensure they are there.
        import_all(admin.company.id)
        
        # Verify count
        count = db.query(PriceItem).filter(PriceItem.company_id == admin.company.id).count()
        print(f"Total items for company {admin.company.id}: {count}")
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"An error occurred: {e}")

    finally:
        db.close()

if __name__ == "__main__":
    run_import()
