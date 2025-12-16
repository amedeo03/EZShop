from sqlalchemy import Column, Float, Integer, String, ForeignKey
from sqlalchemy.orm import mapped_column, relationship

from app.database.database import Base


class ReturnedItemDAO(Base):
    __tablename__ = "returned_items"

    id = mapped_column(ForeignKey("products.id"), primary_key=True)
    return_id = mapped_column(ForeignKey("return_transactions.id"), primary_key=True) 
    quantity = Column(Integer, nullable=False, unique=False)
    returns = relationship("ReturnTransactionDAO", back_populates="lines")
    



