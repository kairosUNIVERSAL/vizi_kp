"""Quick check: what's in the database right now?"""
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.database import SessionLocal
from app.models import PriceItem, Category, Company, User

db = SessionLocal()

# Categories
cats = db.query(Category).all()
print(f"\n=== {len(cats)} Categories ===")
for c in cats:
    count = db.query(PriceItem).filter(PriceItem.category_id == c.id, PriceItem.is_active == True).count()
    total = db.query(PriceItem).filter(PriceItem.category_id == c.id).count()
    print(f"  [{c.id}] {c.name} (is_equipment={c.is_equipment}) → {count} active / {total} total")

# Items summary
total_active = db.query(PriceItem).filter(PriceItem.is_active == True).count()
total_all = db.query(PriceItem).count()
print(f"\n=== Items: {total_active} active / {total_all} total ===")

# Company info
companies = db.query(Company).all()
for comp in companies:
    items = db.query(PriceItem).filter(PriceItem.company_id == comp.id).count()
    print(f"  Company [{comp.id}] {comp.name} → {items} items")

# User info
users = db.query(User).all()
for u in users:
    comp_name = u.company.name if u.company else "NO COMPANY"
    comp_id = u.company_id
    print(f"  User [{u.id}] {u.email} → company_id={comp_id} ({comp_name})")

# Sample items
print("\n=== First 5 items ===")
items = db.query(PriceItem).filter(PriceItem.is_active == True).limit(5).all()
for item in items:
    cat_name = item.category.name if item.category else "NO CAT"
    print(f"  [{item.id}] {item.name} | {item.price} {item.unit} | cat={cat_name} | company_id={item.company_id}")

db.close()
