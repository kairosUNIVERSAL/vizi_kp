from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
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
    company: Optional[CompanyResponse] = None

    class Config:
        from_attributes = True
