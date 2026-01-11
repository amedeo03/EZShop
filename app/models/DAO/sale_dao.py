from sqlalchemy import Column, DateTime, Float, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.database import Base


class SaleDAO(Base):
    __tablename__ = "sales"

    id = Column(Integer, primary_key=True, autoincrement=True)
    status = Column(String, nullable=False, unique=False)
    discount_rate = Column(Float, nullable=False, unique=False)
    created_at = Column(
        DateTime(timezone=True), nullable=True, unique=False, server_default=func.now()
    )
    closed_at = Column(DateTime, nullable=True, unique=False)

    lines = relationship(
        "SoldProductDAO",
        back_populates="sale",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
