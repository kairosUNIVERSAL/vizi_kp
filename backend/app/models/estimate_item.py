from sqlalchemy import Column, Integer, String, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from app.database import Base

class EstimateItem(Base):
    __tablename__ = "estimate_items"
    
    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(Integer, ForeignKey("estimate_rooms.id"), nullable=False)
    price_item_id = Column(Integer, ForeignKey("price_items.id"), nullable=True)  # Null для кастомных
    name = Column(String(255), nullable=False)
    unit = Column(String(20), nullable=False)
    quantity = Column(Numeric(10, 2), nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    sum = Column(Numeric(12, 2), nullable=False)
    
    # Relationships
    room = relationship("EstimateRoom", back_populates="items")
    price_item = relationship("PriceItem")
