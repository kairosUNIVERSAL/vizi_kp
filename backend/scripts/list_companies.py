"""
Diagnostic script to list users and their company IDs.
Run: docker compose exec backend python scripts/list_companies.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.models import User, Company, PriceItem

def check():
    db = SessionLocal()
    try:
        users = db.query(User).all()
        print("\n=== SYSTEM USERS & COMPANIES ===")
        for u in users:
            comp_id = u.company.id if u.company else "NONE"
            items_count = db.query(PriceItem).filter(PriceItem.company_id == comp_id).count() if comp_id != "NONE" else 0
            print(f"User: {u.email} | Admin: {u.is_admin} | Company ID: {comp_id} | Price Items: {items_count}")
        
    finally:
        db.close()

if __name__ == "__main__":
    check()
