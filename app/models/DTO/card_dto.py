from pydantic import BaseModel
from typing import Optional

class CardDTO(BaseModel):
    card_id: Optional[str] =None
    points: Optional[int]=0


class CardResponseDTO(BaseModel):
    card_id: str
    points: Optional[int]=0

class CardCreateDTO(BaseModel):
    card_id: str
    points: Optional[int]=0

class CardUpdateDTO(BaseModel):
    card_id: Optional[str] =""
    points: Optional[int]=-1
