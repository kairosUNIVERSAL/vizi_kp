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

def run_import(target_email=None):
    db = SessionLocal()
    try:
        query = db.query(User).filter(User.is_admin == True)
        if target_email:
            query = query.filter(User.email == target_email)
        
        admins = query.all()
        
        if not admins:
            print(f"Error: No admin user found {'with email ' + target_email if target_email else ''}. Create one first.")
            return

        for admin in admins:
            print(f"\n--- Processing Admin: {admin.email} (Company ID: {admin.company.id if admin.company else 'NEW'}) ---")
            
            if not admin.company:
                # Create company if missing
                from app.models import Company
                admin.company = Company(user_id=admin.id)
                db.add(admin.company)
                db.commit()
                db.refresh(admin)

            print(f"Starting price import (upsert mode) for company_id={admin.company.id}...")
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
    email = sys.argv[1] if len(sys.argv) > 1 else None
    run_import(email)

