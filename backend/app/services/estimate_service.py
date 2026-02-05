from sqlalchemy.orm import Session, joinedload
from app.models import Estimate, EstimateRoom, EstimateItem, EstimateStatus
from app.schemas.estimate import EstimateCreate, EstimateUpdate
from typing import List, Optional

class EstimateService:
    def create_estimate(self, db: Session, company_id: int, estimate_in: EstimateCreate) -> Estimate:
        # Create Estimate
        estimate = Estimate(
            company_id=company_id,
            client_name=estimate_in.client_name,
            client_phone=estimate_in.client_phone,
            client_address=estimate_in.client_address,
            status=estimate_in.status
        )
        db.add(estimate)
        db.commit()
        db.refresh(estimate)
        
        # Create Rooms and Items
        total_area = 0
        total_sum = 0
        
        for room_in in estimate_in.rooms:
            room = EstimateRoom(
                estimate_id=estimate.id,
                name=room_in.name,
                area=room_in.area or 0
            )
            db.add(room)
            db.commit()
            db.refresh(room)
            
            room_subtotal = 0
            for item_in in room_in.items:
                item_sum = float(item_in.quantity) * float(item_in.price)
                item = EstimateItem(
                    room_id=room.id,
                    price_item_id=item_in.price_item_id,
                    name=item_in.name,
                    unit=item_in.unit,
                    quantity=item_in.quantity,
                    price=item_in.price,
                    sum=item_sum
                )
                db.add(item)
                room_subtotal += item_sum
            
            room.subtotal = room_subtotal
            total_area += float(room.area or 0)
            total_sum += room_subtotal
            db.add(room)
            
        estimate.total_area = total_area
        estimate.total_sum = total_sum
        db.add(estimate)
        db.commit()
        db.refresh(estimate)
        return estimate

    def get_estimate(self, db: Session, estimate_id: int):
        # Eager load rooms and items to avoid lazy loading issues
        return db.query(Estimate).options(
            joinedload(Estimate.rooms).joinedload(EstimateRoom.items)
        ).filter(Estimate.id == estimate_id).first()

    def list_estimates(self, db: Session, company_id: int):
        """List all estimates for a company, ordered by creation date descending."""
        return db.query(Estimate).options(
            joinedload(Estimate.rooms).joinedload(EstimateRoom.items)
        ).filter(Estimate.company_id == company_id).order_by(Estimate.created_at.desc()).all()

    def delete_estimate(self, db: Session, estimate_id: int) -> bool:
        """Delete an estimate and all related rooms/items (cascade)."""
        estimate = db.query(Estimate).filter(Estimate.id == estimate_id).first()
        if not estimate:
            return False
        db.delete(estimate)
        db.commit()
        return True

estimate_service = EstimateService()
