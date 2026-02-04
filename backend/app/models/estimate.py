from sqlalchemy import Column, Integer, String, ForeignKey, Numeric, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum

class EstimateStatus(str, enum.Enum):
    DRAFT = "draft"
    COMPLETED = "completed"
    SENT = "sent"
    ACCEPTED = "accepted"
    REJECTED = "rejected"

class Estimate(Base):
    __tablename__ = "estimates"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    client_name = Column(String(255), nullable=False)
    client_phone = Column(String(50), default="")
    client_address = Column(String(500), default="")
    estimate_date = Column(DateTime(timezone=True), server_default=func.now())
    total_area = Column(Numeric(10, 2), default=0)
    total_sum = Column(Numeric(12, 2), default=0)
    status = Column(Enum(EstimateStatus), default=EstimateStatus.DRAFT)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    company = relationship("Company", back_populates="estimates")
    rooms = relationship("EstimateRoom", back_populates="estimate", cascade="all, delete-orphan")
