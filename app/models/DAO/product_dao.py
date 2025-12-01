from sqlalchemy import Column, Integer, String
from app.database.database import Base


class ProductDAO(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, autoincrement=True)
    description = Column(String, nullable=False, unique=False)
    productCode = Column(String, nullable=False, unique=True)
    pricePerUnit = Column(String, nullable=False)
    note = Column(String, nullable=True)
    quantity = Column(Integer, nullable=False)
    position = Column(String, nullable=True)
