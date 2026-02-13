from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ActivityLogResponse(BaseModel):
    id: int
    created_at: datetime
    action: str
    user_id: Optional[int] = None
    user_email: Optional[str] = None
    method: Optional[str] = None
    endpoint: Optional[str] = None
    status_code: Optional[int] = None
    duration_ms: Optional[int] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    details: Optional[str] = None

    class Config:
        from_attributes = True
