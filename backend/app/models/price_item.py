from sqlalchemy import Column, Integer, String, ForeignKey, Numeric, Boolean, Text
from sqlalchemy.orm import relationship
from app.database import Base

class PriceItem(Base):
    __tablename__ = "price_items"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    name = Column(String(255), nullable=False)
    unit = Column(String(20), nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    synonyms = Column(Text, default="")
    is_active = Column(Boolean, default=True)
    is_custom = Column(Boolean, default=False)
    
    # Relationships
    company = relationship("Company", back_populates="price_items")
    category = relationship("Category", back_populates="price_items")
