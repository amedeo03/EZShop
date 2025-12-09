from sqlalchemy import Column, Float, Integer, String, DateTime
from app.database.database import Base

class OrderDAO(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, autoincrement=True)
    product_barcode = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False)
    price_per_unit = Column(Float, nullable=False)
    status = Column(String, nullable=False)  # Will store 'ISSUED', 'PAID', or 'COMPLETED'
    issue_date = Column(DateTime, nullable=True)