from sqlalchemy import Column,ForeignKey, Integer, String, Float
from sqlalchemy.orm import relationship, mapped_column

from app.database.database import Base


class SoldProductDAO(Base):
    __tablename__ = "sold_products"

    id = mapped_column(ForeignKey("products.id"), primary_key=True) 
    sale_id = mapped_column(ForeignKey("sales.id"), primary_key=True)    
    quantity = Column(Integer, nullable=False)
    discount_rate = Column(Float, nullable=False)

    sale = relationship("SaleDAO", back_populates="lines")
    