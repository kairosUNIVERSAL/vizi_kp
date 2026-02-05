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
        # Find the first admin user
        admin = db.query(User).filter(User.is_admin == True).first()
        if not admin:
            print("Error: No admin user found. Create one first.")
            return
        
        if not admin.company:
            print("Error: Admin user has no associated company.")
            return

        print(f"Found admin: {admin.email} (Company ID: {admin.company.id})")
        
        # Clear existing items for this company to avoid "skipped" if they exist
        db.query(PriceItem).filter(PriceItem.company_id == admin.company.id).delete()
        db.commit()
        
        print("Starting clean price import...")
        # Reuse import logic
        import_all(admin.company.id)

        
        print("\nAdmin price list updated successfully!")
        
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    run_import()
