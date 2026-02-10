from sqlalchemy.orm import Session, joinedload
from sqlalchemy.orm import Session, joinedload
from app.models import Estimate, EstimateRoom, EstimateItem, EstimateStatus, PriceItem, Category
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
            status=estimate_in.status,
            discount_pr_work=estimate_in.discount_pr_work,
            discount_equipment=estimate_in.discount_equipment
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
        # Eager load rooms, items, and price_item -> category
        return db.query(Estimate).options(
            joinedload(Estimate.rooms)
            .joinedload(EstimateRoom.items)
            .joinedload(EstimateItem.price_item)
            .joinedload(PriceItem.category)
        ).filter(Estimate.id == estimate_id).first()

    def list_estimates(self, db: Session, company_id: int):
        """List all estimates for a company, ordered by creation date descending."""
        return db.query(Estimate).options(
            joinedload(Estimate.rooms)
            .joinedload(EstimateRoom.items)
            .joinedload(EstimateItem.price_item)
            .joinedload(PriceItem.category)
        ).filter(Estimate.company_id == company_id).order_by(Estimate.created_at.desc()).all()

    def delete_estimate(self, db: Session, estimate_id: int) -> bool:
        """Delete an estimate and all related rooms/items (cascade)."""
        estimate = db.query(Estimate).filter(Estimate.id == estimate_id).first()
        if not estimate:
            return False
        db.delete(estimate)
        db.commit()
        return True
    def update_estimate(self, db: Session, estimate_id: int, estimate_in: EstimateUpdate) -> Optional[Estimate]:
        """Update an existing estimate. Replaces rooms/items if provided."""
        estimate = self.get_estimate(db, estimate_id)
        if not estimate:
            return None

        # Update scalar fields
        if estimate_in.client_name is not None:
            estimate.client_name = estimate_in.client_name
        if estimate_in.client_phone is not None:
            estimate.client_phone = estimate_in.client_phone
        if estimate_in.client_address is not None:
            estimate.client_address = estimate_in.client_address
        if estimate_in.status is not None:
            estimate.status = estimate_in.status
        if estimate_in.last_step is not None:
            estimate.last_step = estimate_in.last_step
        if estimate_in.discount_pr_work is not None:
            estimate.discount_pr_work = estimate_in.discount_pr_work
        if estimate_in.discount_equipment is not None:
            estimate.discount_equipment = estimate_in.discount_equipment

        # Replace rooms and items if provided
        if estimate_in.rooms is not None:
            # Delete existing rooms (cascade deletes items)
            # ... (rest of the logic remains the same, assuming it was correct)
            for room in list(estimate.rooms):
                db.delete(room)
            db.flush()

            total_area = 0
            total_sum = 0
            
            # Note: We need to recalculate total_sum based on discounts if we want it stored "net" or "gross"?
            # Typically total_sum in DB is "Gross" or "Final"? 
            # PDF calculates final. Let's store Gross here as sum of items, 
            # or we should store the final discounted sum?
            # The current logic sums up room_subtotal.
            # Let's keep total_sum as sum of items (Gross) for now, 
            # and allow specific fields for discounts. 
            # Real "To Pay" will be calculated on fly or we add a `final_sum` column?
            # For now, let's keep total_sum as is (sum of items).

            for room_in in estimate_in.rooms:
                room = EstimateRoom(
                    estimate_id=estimate.id,
                    name=room_in.name,
                    area=room_in.area or 0
                )
                db.add(room)
                db.flush()

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

        db.commit()
        db.refresh(estimate)
        return estimate

estimate_service = EstimateService()
