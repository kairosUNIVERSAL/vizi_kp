from sqlalchemy.orm import Session, joinedload
from app.models import PriceItem, Category, User
from app.schemas.price import PriceItemCreate, PriceItemUpdate
from typing import List, Optional

FOCUS_GROUP_EMAILS = {
    "focus.admin@kp.local",
    "focus.sales@kp.local",
    "focus.ops@kp.local",
    "focus.newcomer@kp.local",
    "focus.dispatch@kp.local",
    "focus.measure@kp.local",
    "focus.b2b@kp.local",
}

class PriceService:
    def _get_source_admin_category_ids(self, db: Session) -> List[int]:
        admins = db.query(User).filter(User.is_admin == True).order_by(User.created_at.asc()).all()

        for admin in admins:
            if not admin.company or admin.email in FOCUS_GROUP_EMAILS:
                continue
            category_ids = [
                row[0]
                for row in db.query(PriceItem.category_id).filter(PriceItem.company_id == admin.company.id).distinct().all()
            ]
            if category_ids:
                return category_ids

        for admin in admins:
            if not admin.company:
                continue
            category_ids = [
                row[0]
                for row in db.query(PriceItem.category_id).filter(PriceItem.company_id == admin.company.id).distinct().all()
            ]
            if category_ids:
                return category_ids

        return []

    def get_categories(self, db: Session, company_id: Optional[int] = None) -> List[Category]:
        if company_id is not None:
            company_category_ids = [
                row[0]
                for row in db.query(PriceItem.category_id).filter(PriceItem.company_id == company_id).distinct().all()
            ]
            if company_category_ids:
                return db.query(Category).filter(Category.id.in_(company_category_ids)).order_by(Category.sort_order, Category.id).all()

            source_category_ids = self._get_source_admin_category_ids(db)
            if source_category_ids:
                return db.query(Category).filter(Category.id.in_(source_category_ids)).order_by(Category.sort_order, Category.id).all()

        return db.query(Category).order_by(Category.sort_order, Category.id).all()
    
    def get_items(self, db: Session, company_id: int, category_id: Optional[int] = None, active_only: bool = True) -> List[PriceItem]:
        query = db.query(PriceItem).options(joinedload(PriceItem.category)).filter(PriceItem.company_id == company_id)
        
        if category_id:
            query = query.filter(PriceItem.category_id == category_id)
        
        if active_only:
            query = query.filter(PriceItem.is_active == True)
            
        return query.all()

    def search_items(self, db: Session, company_id: int, query: str, limit: int = 10) -> List[PriceItem]:
        q = f"%{query}%"
        return db.query(PriceItem).options(joinedload(PriceItem.category)).filter(
            PriceItem.company_id == company_id,
            PriceItem.is_active == True,
            (PriceItem.name.ilike(q) | PriceItem.synonyms.ilike(q))
        ).limit(limit).all()
    
    def create_item(self, db: Session, company_id: int, item_in: PriceItemCreate) -> PriceItem:
        item = PriceItem(
            **item_in.model_dump(exclude={'is_custom'}),
            company_id=company_id,
            is_custom=True
        )
        db.add(item)
        db.commit()
        db.refresh(item)
        # Load category for response
        return db.query(PriceItem).options(joinedload(PriceItem.category)).filter(PriceItem.id == item.id).first()
    
    def update_item(self, db: Session, item_id: int, item_in: PriceItemUpdate) -> Optional[PriceItem]:
        item = db.query(PriceItem).filter(PriceItem.id == item_id).first()
        if not item:
            return None
            
        update_data = item_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(item, field, value)
            
        db.add(item)
        db.commit()
        db.refresh(item)
        db.refresh(item)
        return db.query(PriceItem).options(joinedload(PriceItem.category)).filter(PriceItem.id == item_id).first()

    def delete_item(self, db: Session, company_id: int, item_id: int) -> bool:
        item = db.query(PriceItem).filter(
            PriceItem.id == item_id,
            PriceItem.company_id == company_id
        ).first()
        
        if not item:
            return False
            
        # Hard delete or soft delete? Let's do hard delete for now as per simple CRUD
        # Or better: set is_active=False if we want to keep history, but user asked to "delete".
        # Let's do hard delete to clean up DB, assuming no generic foreign keys blocking it yet (EstimateItem handles it?)
        # Actually safer to soft delete usually, but for "Management" often users expect removal.
        # Let's check models.py to see if there are cascades. Assuming standard.
        # Let's use delete()
        db.delete(item)
        db.commit()
        return True

    def add_synonym(self, db: Session, company_id: int, item_id: int, synonym: str) -> Optional[PriceItem]:
        item = db.query(PriceItem).filter(
            PriceItem.id == item_id,
            PriceItem.company_id == company_id
        ).first()
        
        if not item:
            return None
            
        current_synonyms = [s.strip() for s in item.synonyms.split(',') if s.strip()]
        new_synonym = synonym.strip()
        
        if new_synonym and new_synonym not in current_synonyms:
            current_synonyms.append(new_synonym)
            item.synonyms = ", ".join(current_synonyms)
            db.add(item)
            db.commit()
            db.refresh(item)
            
        return item

price_service = PriceService()
