from typing import Optional

from pydantic import BaseModel, Field


class SoldProductDTO(BaseModel):
    id: Optional[int] = None
    productCode: str
    pricePerUnit: float = 0.0
    quantity: int = 1
