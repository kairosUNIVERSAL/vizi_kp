"""Admin API endpoints for user management and statistics."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Any, List

from app.api.deps import get_current_active_user, get_db
from app.models import User, Company, Estimate
from app.schemas.user import UserCreate, UserResponse, UserAdminResponse
from app.services.auth_service import auth_service

router = APIRouter()


def require_admin(current_user: User = Depends(get_current_active_user)) -> User:
    """Dependency that requires admin privileges."""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


@router.get("/users", response_model=List[UserAdminResponse])
def list_users(
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
) -> Any:
    """Get all users with statistics."""
    users = db.query(User).order_by(User.created_at.desc()).all()
    
    result = []
    for user in users:
        # Count estimates for each user
        estimates_count = 0
        if user.company:
            estimates_count = db.query(func.count(Estimate.id)).filter(
                Estimate.company_id == user.company.id
            ).scalar() or 0
        
        user_dict = {
            "id": user.id,
            "email": user.email,
            "is_active": user.is_active,
            "is_admin": user.is_admin,
            "created_at": user.created_at,
            "total_tokens_used": user.total_tokens_used or 0,
            "total_api_cost": user.total_api_cost or 0,
            "company": user.company,
            "estimates_count": estimates_count
        }
        result.append(user_dict)
    
    return result


@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    user_in: UserCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
) -> Any:
    """Create a new user (admin only)."""
    # Check if user exists
    existing = db.query(User).filter(User.email == user_in.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )
    
    # Create user
    user = auth_service.create_user(db, user_in.email, user_in.password, user_in.is_admin)
    return user


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
) -> None:
    """Delete a user (admin only)."""
    if user_id == admin.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete yourself"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Delete associated company, estimates, price items (cascade)
    if user.company:
        db.delete(user.company)
    
    db.delete(user)
    db.commit()
    return None


@router.get("/stats")
def get_admin_stats(
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
) -> Any:
    """Get aggregate statistics for admin dashboard."""
    total_users = db.query(func.count(User.id)).scalar() or 0
    total_estimates = db.query(func.count(Estimate.id)).scalar() or 0
    total_tokens = db.query(func.sum(User.total_tokens_used)).scalar() or 0
    total_cost = db.query(func.sum(User.total_api_cost)).scalar() or 0
    
    return {
        "total_users": total_users,
        "total_estimates": total_estimates,
        "total_tokens_used": total_tokens,
        "total_api_cost": float(total_cost) if total_cost else 0
    }
