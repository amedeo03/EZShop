from sqlalchemy import Column, Float, ForeignKey, Integer, String
from sqlalchemy.orm import mapped_column, relationship

from app.database.database import Base


class SoldProductDAO(Base):
    __tablename__ = "sold_products"

    id = mapped_column(ForeignKey("products.id"), primary_key=True)
    sale_id = mapped_column(ForeignKey("sales.id"), primary_key=True)
    product_barcode = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False)
    price_per_unit = Column(Float, nullable=False)
    discount_rate = Column(Float, nullable=False)

    sale = relationship("SaleDAO", back_populates="lines")
