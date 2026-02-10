"""
Definitive cleanup: keep ONLY items in the 4 correct categories
(Полотна, Профили, Услуги, Оборудование) and delete everything else.
"""
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.database import SessionLocal
from app.models import PriceItem, Category, EstimateItem


VALID_CATEGORIES = {"полотна", "профили", "услуги", "оборудование"}


def cleanup():
    db = SessionLocal()
    try:
        # 1. Find valid category IDs
        all_cats = db.query(Category).all()
        valid_cat_ids = set()
        invalid_cats = []

        for cat in all_cats:
            if cat.name.lower() in VALID_CATEGORIES:
                valid_cat_ids.add(cat.id)
                print(f"  VALID category: {cat.name} (ID={cat.id}, is_equipment={cat.is_equipment})")
            else:
                invalid_cats.append(cat)
                print(f"  INVALID category: {cat.name} (ID={cat.id}) — will be cleaned")

        # 2. Delete items NOT in valid categories (or deactivated duplicates)
        all_items = db.query(PriceItem).all()
        deleted_items = 0
        kept_items = 0
        kept_linked = 0

        for item in all_items:
            should_delete = (item.category_id not in valid_cat_ids) or (not item.is_active)

            if should_delete:
                # Check if linked to estimate
                has_estimate = db.query(EstimateItem).filter(
                    EstimateItem.price_item_id == item.id
                ).first()

                if has_estimate:
                    kept_linked += 1
                    print(f"  KEPT (estimate link): [{item.id}] {item.name}")
                else:
                    db.delete(item)
                    deleted_items += 1
            else:
                kept_items += 1

        db.commit()
        print(f"\nItems: deleted {deleted_items}, kept active {kept_items}, kept linked {kept_linked}")

        # 3. Delete invalid categories (now empty)
        for cat in invalid_cats:
            remaining = db.query(PriceItem).filter(PriceItem.category_id == cat.id).count()
            if remaining == 0:
                db.delete(cat)
                print(f"  Deleted empty category: {cat.name}")
            else:
                print(f"  KEPT category {cat.name} ({remaining} linked items remain)")

        db.commit()

        # 4. Summary
        final_items = db.query(PriceItem).filter(PriceItem.is_active == True).count()
        final_cats = db.query(Category).count()
        print(f"\n=== FINAL: {final_items} active items in {final_cats} categories ===")

        # Show per-category breakdown
        for cat in db.query(Category).order_by(Category.name).all():
            count = db.query(PriceItem).filter(
                PriceItem.category_id == cat.id,
                PriceItem.is_active == True
            ).count()
            print(f"  {cat.name}: {count} items (is_equipment={cat.is_equipment})")

    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    cleanup()
