from sqlalchemy import Column, Integer, String, JSON
from sqlalchemy.orm import relationship
from app.database.database import Base


class CardDAO(Base):
    __tablename__ = "cards"

    cardId = Column(String, primary_key=True, nullable=False)
    points=Column(Integer, nullable=False,default=0)

    customer = relationship("CustomerDAO", back_populates="card", uselist=False)