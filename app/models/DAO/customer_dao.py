from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database.database import Base


class CustomerDAO(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    cardId=Column(String,ForeignKey("cards.cardId"), nullable=True)
    
    card=relationship("CardDAO",back_populates="customer", uselist=False)