from sqlalchemy import Column, Integer, String, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from app.database import Base

class Company(Base):
    __tablename__ = "companies"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    name = Column(String(255), default="")
    phone = Column(String(50), default="")
    city = Column(String(100), default="")
    warranty_material = Column(Integer, default=15)  # лет
    warranty_work = Column(Integer, default=3)       # лет
    validity_days = Column(Integer, default=14)      # дней
    discount = Column(Numeric(5, 2), default=5)      # процент
    
    # Relationships
    user = relationship("User", back_populates="company")
    price_items = relationship("PriceItem", back_populates="company")
    estimates = relationship("Estimate", back_populates="company")
