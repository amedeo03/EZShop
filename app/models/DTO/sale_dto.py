from typing import List, Optional

from pydantic import BaseModel
from sold_product_dto import SoldProductDTO


class SaleDTO(BaseModel):
    id: Optional[int] = None
    status: str = "OPEN"
    discount_rate: float = 0.0
    created_at: Optional[str] = None
    closed_at: Optional[str] = None
    lines: List[SoldProductDTO] = list()