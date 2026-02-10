from pydantic import BaseModel
from typing import Optional, List
from decimal import Decimal

# Category Schemas
class CategoryBase(BaseModel):
    name: str
    slug: str
    sort_order: int = 0
    is_system: bool = True
    is_equipment: bool = False

class CategoryResponse(CategoryBase):
    id: int

    class Config:
        from_attributes = True

# PriceItem Schemas
class PriceItemBase(BaseModel):
    category_id: int
    name: str
    unit: str
    price: Decimal
    synonyms: Optional[str] = ""
    is_active: bool = True
    is_custom: bool = False

class PriceItemCreate(PriceItemBase):
    pass

class PriceItemUpdate(BaseModel):
    price: Optional[Decimal] = None
    is_active: Optional[bool] = None
    synonyms: Optional[str] = None
    name: Optional[str] = None
    unit: Optional[str] = None

class PriceItemResponse(PriceItemBase):
    id: int
    category_name: Optional[str] = None # Helper field

    class Config:
        from_attributes = True

class PriceItemListResponse(BaseModel):
    items: List[PriceItemResponse]
    total: int
