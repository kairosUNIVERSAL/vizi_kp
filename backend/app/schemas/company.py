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
    
    # Extended profile
    logo_path: Optional[str] = None
    address: Optional[str] = ""
    website: Optional[str] = ""
    messenger_contact: Optional[str] = ""
    messenger_type: Optional[str] = "telegram"
    
    # Payment details
    inn: Optional[str] = ""
    kpp: Optional[str] = ""
    bank_name: Optional[str] = ""
    bank_account: Optional[str] = ""
    bank_bik: Optional[str] = ""
    bank_corr: Optional[str] = ""

class CompanyCreate(CompanyBase):
    pass

class CompanyUpdate(CompanyBase):
    pass

class CompanyResponse(CompanyBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True

