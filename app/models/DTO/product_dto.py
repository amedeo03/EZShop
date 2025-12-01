from pydantic import BaseModel, Field
from typing import Optional


class ProductTypeDTO(BaseModel):
    id: Optional[int] = None
    description: str = Field(min_length=1)
    productCode: str = Field(min_length=1)
    pricePerUnit: float
    note: str = Field(min_length=1)
    quantity: int
    position: str = None
