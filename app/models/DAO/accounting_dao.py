from sqlalchemy import Column, Integer, Float
from app.database.database import Base


class AccountingDAO(Base):
    __tablename__ = "accounting"
    id = Column(Integer, primary_key=True, autoincrement=True)
    balance = Column(Float, nullable=False, default=0.0)