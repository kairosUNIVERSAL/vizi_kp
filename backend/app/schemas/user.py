from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from decimal import Decimal
from .company import CompanyResponse

class UserBase(BaseModel):
    email: EmailStr
    is_active: bool = True
    is_admin: bool = False

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None

class UserResponse(UserBase):
    id: int
    created_at: datetime
    total_tokens_used: int = 0
    total_api_cost: Decimal = Decimal(0)
    company: Optional[CompanyResponse] = None

    class Config:
        from_attributes = True

# Admin-specific schemas
class UserAdminResponse(UserResponse):
    """Extended user response for admin panel"""
    estimates_count: int = 0

