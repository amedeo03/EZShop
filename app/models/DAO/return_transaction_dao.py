from sqlalchemy import Column, Float, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import mapped_column, relationship
from sqlalchemy.sql import func

from app.database.database import Base


class ReturnTransactionDAO(Base):
    __tablename__ = "return_transactions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    sale_id = mapped_column(ForeignKey("sales.id"), primary_key=True)
    status = Column(String, nullable=False, unique=False)
    created_at = Column(
        DateTime(timezone=True), nullable=False, unique=False, server_default=func.now()
    )
    closed_at = Column(DateTime, nullable=True, unique=False)
    lines = relationship(
        "ReturnedItemDAO",
        back_populates="returns",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    
