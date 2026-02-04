from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Any, List, Optional

from app.api.deps import get_current_active_user
from app.database import get_db
from app.services import price_service
from app.schemas.price import (
    CategoryResponse, PriceItemResponse, PriceItemListResponse,
    PriceItemCreate, PriceItemUpdate
)
from app.models import User

router = APIRouter()

@router.get("/categories", response_model=List[CategoryResponse])
def get_categories(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Get all categories.
    """
    return price_service.get_categories(db)

@router.get("/items", response_model=PriceItemListResponse)
def get_items(
    category_id: Optional[int] = None,
    active_only: bool = True,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Get price items.
    """
    if not current_user.company:
        raise HTTPException(status_code=400, detail="User has no company")
        
    items = price_service.get_items(db, current_user.company.id, category_id, active_only)
    return {"items": items, "total": len(items)}

@router.post("/items", response_model=PriceItemResponse, status_code=201)
def create_item(
    item_in: PriceItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    if not current_user.company:
        raise HTTPException(status_code=400, detail="User has no company")
    return price_service.create_item(db, current_user.company.id, item_in)
