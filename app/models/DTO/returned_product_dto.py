from typing import Optional
from pydantic import BaseModel, ConfigDict

class ReturnedProductDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: Optional[int] = None
    return_id: int = None
    product_barcode: str = None
    quantity: int = 1
    price_per_unit: float = 0.0
