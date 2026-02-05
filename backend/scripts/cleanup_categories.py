"""
Script to clean up old categories and keep only 4 main ones.
Run: docker compose exec backend python scripts/cleanup_categories.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import PriceItem, Category

# Only these 4 categories should remain
KEEP_CATEGORIES = ['polotna', 'uslugi', 'osveshenie', 'profili']

def cleanup_categories():
    db = SessionLocal()
    
    try:
        # 1. First, ensure 4 main categories exist
        print("\n=== Ensuring 4 main categories exist ===")
        main_categories = {
            "polotna": "Полотна",
            "uslugi": "Услуги", 
            "osveshenie": "Освещение",
            "profili": "Профили"
        }
        
        category_ids = {}
        for i, (slug, name) in enumerate(main_categories.items()):
            cat = db.query(Category).filter(Category.slug == slug).first()
            if not cat:
                cat = Category(name=name, slug=slug, sort_order=i+1, is_system=False)
                db.add(cat)
                db.commit()
                db.refresh(cat)
                print(f"  Created: {name}")
            else:
                print(f"  Exists: {name}")
            category_ids[slug] = cat.id
        
        # 2. Get all categories that should be deleted
        print("\n=== Finding old categories to delete ===")
        old_categories = db.query(Category).filter(
            ~Category.slug.in_(KEEP_CATEGORIES)
        ).all()
        
        print(f"  Found {len(old_categories)} old categories to delete")
        
        # 3. Reassign items from old categories to new ones based on item names
        print("\n=== Reassigning items ===")
        items_with_old_cats = db.query(PriceItem).filter(
            PriceItem.category_id.in_([c.id for c in old_categories])
        ).all()
        
        for item in items_with_old_cats:
            name_lower = item.name.lower()
            
            # Determine new category based on item name
            new_category_slug = None
            
            # Полотна keywords
            if any(kw in name_lower for kw in ['msd', 'bauf', 'pongs', 'deken', 'descor', 'clipso', 'полотно', 'мат ', 'сатин', 'глянец']):
                new_category_slug = 'polotna'
            # Освещение keywords
            elif any(kw in name_lower for kw in ['светильник', 'лампа', 'люстра', 'лента led', 'блок питания', 'термокольц', 'закладная универс', 'подвес для закладной', 'перфолента', 'рассеиватель', 'профиль алюмин']):
                new_category_slug = 'osveshenie'
            # Профили keywords  
            elif any(kw in name_lower for kw in ['профиль', 'eurokraab', 'kraab', 'бизон', 'карниз', 'гарпун', 'маскировочная', 'парящий', 'световой линии', 'трек', 'slott', 'flexy', 'разделител']):
                new_category_slug = 'profili'
            # All else -> Услуги
            else:
                new_category_slug = 'uslugi'
            
            item.category_id = category_ids[new_category_slug]
            print(f"  {item.name} -> {main_categories[new_category_slug]}")
        
        db.commit()
        
        # 4. Delete old categories
        print("\n=== Deleting old categories ===")
        for cat in old_categories:
            print(f"  Deleting: {cat.name} ({cat.slug})")
            db.delete(cat)
        
        db.commit()
        
        print("\n=== Cleanup Complete ===")
        
        # Show final state
        final_categories = db.query(Category).order_by(Category.sort_order).all()
        print(f"\nRemaining categories ({len(final_categories)}):")
        for cat in final_categories:
            item_count = db.query(PriceItem).filter(PriceItem.category_id == cat.id).count()
            print(f"  {cat.name} ({cat.slug}): {item_count} items")
        
    finally:
        db.close()


if __name__ == '__main__':
    print("Category cleanup script")
    print("This will:")
    print("  1. Keep only 4 main categories: Полотна, Услуги, Освещение, Профили")
    print("  2. Reassign items from old categories to new ones")
    print("  3. Delete all other categories")
    print("")
    
    confirm = input("Proceed? (y/n): ").strip().lower()
    if confirm == 'y':
        cleanup_categories()
    else:
        print("Cancelled.")
