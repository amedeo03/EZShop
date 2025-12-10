from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict

from .sold_product_dto import SoldProductDTO


class SaleDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int]
    status: str
    discount_rate: float = 0.0
    created_at: datetime
    closed_at: Optional[datetime] = None
    lines: List[SoldProductDTO] = []
