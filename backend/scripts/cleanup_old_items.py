"""
NUCLEAR CLEANUP: Unlink estimates from old items, delete ALL price items
and categories, then re-import fresh from Excel.
"""
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.database import SessionLocal
from app.models import PriceItem, Category, EstimateItem


def nuke_and_report():
    db = SessionLocal()
    try:
        # 1. Unlink all estimate items from price items
        linked = db.query(EstimateItem).filter(
            EstimateItem.price_item_id.isnot(None)
        ).count()
        if linked > 0:
            db.query(EstimateItem).filter(
                EstimateItem.price_item_id.isnot(None)
            ).update({"price_item_id": None})
            db.commit()
            print(f"Unlinked {linked} estimate items from old price items")

        # 2. Delete ALL price items
        deleted_items = db.query(PriceItem).delete()
        db.commit()
        print(f"Deleted {deleted_items} price items")

        # 3. Delete ALL categories
        deleted_cats = db.query(Category).delete()
        db.commit()
        print(f"Deleted {deleted_cats} categories")

        print("\n=== Database is clean. Now run import_excel.py ===")

    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    nuke_and_report()
