from sqlalchemy import Column, Float, Integer, String

from app.database.database import Base


class ProductDAO(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, autoincrement=True)
    description = Column(String, nullable=False, unique=False)
    barcode = Column(String, nullable=False, unique=True)
    price_per_unit = Column(Float, nullable=False)
    note = Column(String, nullable=True)
    quantity = Column(Integer, nullable=True)
    position = Column(String, nullable=True)
