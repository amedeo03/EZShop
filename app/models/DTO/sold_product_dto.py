from pydantic import BaseModel, ConfigDict


class SoldProductDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    sale_id: int
    product_barcode: str
    quantity: int = 1
    price_per_unit: float
    discount_rate: float = 0.0
