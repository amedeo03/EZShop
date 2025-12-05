from pydantic import BaseModel
from typing import Optional

class CardDTO(BaseModel):
    cardId: Optional[str] =None
    points: Optional[int]=0


class CardResponseDTO(BaseModel):
    cardId: str
    points: Optional[int]=0

class CardCreateDTO(BaseModel):
    cardId: str
    points: Optional[int]=0