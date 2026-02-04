from pydantic import BaseModel, Field
from typing import Optional
from decimal import Decimal

class CompanyBase(BaseModel):
    name: Optional[str] = ""
    phone: Optional[str] = ""
    city: Optional[str] = ""
    warranty_material: int = 15
    warranty_work: int = 3
    validity_days: int = 14
    discount: Decimal = 5

class CompanyCreate(CompanyBase):
    pass

class CompanyUpdate(CompanyBase):
    pass

class CompanyResponse(CompanyBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True
