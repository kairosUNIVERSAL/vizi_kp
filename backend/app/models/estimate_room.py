from sqlalchemy import Column, Integer, String, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from app.database import Base

class EstimateRoom(Base):
    __tablename__ = "estimate_rooms"
    
    id = Column(Integer, primary_key=True, index=True)
    estimate_id = Column(Integer, ForeignKey("estimates.id"), nullable=False)
    name = Column(String(100), nullable=False)
    area = Column(Numeric(10, 2), default=0)
    subtotal = Column(Numeric(12, 2), default=0)
    
    # Relationships
    estimate = relationship("Estimate", back_populates="rooms")
    items = relationship("EstimateItem", back_populates="room", cascade="all, delete-orphan")
