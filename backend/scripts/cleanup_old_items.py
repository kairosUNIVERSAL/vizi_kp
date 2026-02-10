"""
Cleanup script: hard-delete all deactivated price items and orphaned categories.
Run AFTER import_excel.py to remove old seed data.
"""
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.database import SessionLocal
from app.models import PriceItem, Category, EstimateItem

def cleanup():
    db = SessionLocal()
    try:
        # Find deactivated items that have NO linked estimate items
        inactive_items = db.query(PriceItem).filter(PriceItem.is_active == False).all()

        deleted = 0
        kept = 0
        for item in inactive_items:
            has_estimates = db.query(EstimateItem).filter(
                EstimateItem.price_item_id == item.id
            ).first()

            if has_estimates:
                kept += 1
                print(f"  KEPT (linked to estimate): {item.name}")
            else:
                db.delete(item)
                deleted += 1

        db.commit()
        print(f"\nDeleted {deleted} old items, kept {kept} (linked to estimates)")

        # Delete orphaned categories (no items left)
        all_cats = db.query(Category).all()
        orphans_deleted = 0
        for cat in all_cats:
            item_count = db.query(PriceItem).filter(PriceItem.category_id == cat.id).count()
            if item_count == 0:
                print(f"  Deleting empty category: {cat.name}")
                db.delete(cat)
                orphans_deleted += 1

        db.commit()
        print(f"Deleted {orphans_deleted} empty categories")

        # Summary
        active_count = db.query(PriceItem).filter(PriceItem.is_active == True).count()
        cat_count = db.query(Category).count()
        print(f"\nFinal state: {active_count} active items in {cat_count} categories")

    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    cleanup()
