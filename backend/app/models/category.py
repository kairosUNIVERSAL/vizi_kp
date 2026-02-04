from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from app.database import Base

class Category(Base):
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    slug = Column(String(50), unique=True, nullable=False)
    sort_order = Column(Integer, default=0)
    is_system = Column(Boolean, default=True)  # Системная или пользовательская
    
    # Relationships
    price_items = relationship("PriceItem", back_populates="category")
