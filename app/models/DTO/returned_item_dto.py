from typing import Optional
from pydantic import BaseModel

class ReturnedItemDTO(BaseModel):
    id: Optional[int] = None
    return_id: int = None
    product_barcode: str = None
    quantity: int = 1
    price_per_unit: float = 0.0
