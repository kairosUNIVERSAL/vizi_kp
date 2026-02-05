from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from decimal import Decimal
from datetime import datetime
from enum import Enum

class EstimateStatus(str, Enum):
    DRAFT = "draft"
    COMPLETED = "completed"
    SENT = "sent"
    ACCEPTED = "accepted"
    REJECTED = "rejected"

# Estimate Item
class EstimateItemBase(BaseModel):
    name: str
    unit: str
    quantity: Decimal
    price: Decimal
    sum: Optional[Decimal] = None
    price_item_id: Optional[int] = None

class EstimateItemCreate(EstimateItemBase):
    pass

class EstimateItemResponse(EstimateItemBase):
    id: int
    room_id: int
    sum: Decimal

    class Config:
        from_attributes = True

# Estimate Room
class EstimateRoomBase(BaseModel):
    name: str
    area: Decimal = 0
    subtotal: Optional[Decimal] = None

class EstimateRoomCreate(EstimateRoomBase):
    items: List[EstimateItemCreate] = []

class EstimateRoomResponse(EstimateRoomBase):
    id: int
    estimate_id: int
    subtotal: Decimal
    items: List[EstimateItemResponse] = []

    class Config:
        from_attributes = True

# Estimate
class EstimateBase(BaseModel):
    client_name: str
    client_phone: Optional[str] = ""
    client_address: Optional[str] = ""
    status: EstimateStatus = EstimateStatus.DRAFT

class EstimateCreate(EstimateBase):
    rooms: List[EstimateRoomCreate] = []

class EstimateUpdate(BaseModel):
    client_name: Optional[str] = None
    client_phone: Optional[str] = None
    client_address: Optional[str] = None
    status: Optional[EstimateStatus] = None
    rooms: Optional[List[EstimateRoomCreate]] = None

class EstimateResponse(EstimateBase):
    id: int
    company_id: int
    estimate_date: datetime
    total_area: Decimal
    total_sum: Decimal
    created_at: datetime
    rooms: List[EstimateRoomResponse] = []

    class Config:
        from_attributes = True

# AI Parsing Types
class UnknownItem(BaseModel):
    original_text: Optional[str] = None  # May be missing in some AI responses
    name: Optional[str] = None  # AI sometimes returns 'name' instead
    quantity: Optional[Decimal] = None
    suggested_quantity: Optional[Decimal] = None
    suggested_unit: Optional[str] = None
    suggested_category_id: Optional[int] = None
    suggested_category_name: Optional[str] = None

class EstimateParseResponse(BaseModel):
    rooms: List[Dict[str, Any]] = []
    unknown_items: List[UnknownItem] = []
    total_area: Decimal = 0
    total_sum: Decimal = 0
