from pydantic import BaseModel
from typing import Optional
from .card_dto import CardDTO,CardUpdateDTO

class CustomerDTO(BaseModel):
    id: Optional[int] = None
    name: str 
    card: Optional[CardDTO]=None


class CustomerResponseDTO(BaseModel):
    id: Optional[int] = None
    name: str
    card: Optional[CardDTO]=None

class CustomerCreateDTO(BaseModel):
    id: Optional[int] = None
    name: Optional[str]=None 
    card: Optional[CardDTO] = None

class CustomerUpdateDTO(BaseModel):
    id: Optional[int] = None
    name: str 
    card: Optional[CardUpdateDTO] =None
