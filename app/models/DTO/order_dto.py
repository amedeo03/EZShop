from typing import Optional
from datetime import datetime
from pydantic import BaseModel

class OrderDTO(BaseModel):
    id: Optional[int] = None
    product_barcode: str
    quantity: int
    price_per_unit: float
    status: str
    issue_date: Optional[datetime] = None