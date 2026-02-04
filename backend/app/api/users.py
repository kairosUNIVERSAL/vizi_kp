from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Any

from app.api.deps import get_current_active_user
from app.database import get_db
from app.schemas.user import UserResponse
from app.schemas.company import CompanyUpdate, CompanyResponse
from app.models import User, Company

router = APIRouter()

@router.get("/me", response_model=UserResponse)
def read_user_me(
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get current user.
    """
    return current_user

@router.put("/me/company", response_model=CompanyResponse)
def update_company(
    company_in: CompanyUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Update user's company info.
    """
    company = current_user.company
    if not company:
        # Create if not exists (though it should exist from registration)
        company = Company(user_id=current_user.id)
        db.add(company)
        db.commit()
    
    update_data = company_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(company, field, value)
    
    db.add(company)
    db.commit()
    db.refresh(company)
    return company
