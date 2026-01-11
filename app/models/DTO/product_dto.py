from typing import Optional

from pydantic import BaseModel


class ProductTypeDTO(BaseModel):
    id: Optional[int] = None
    description: str = None
    barcode: str = None
    price_per_unit: float = None
    note: str = None
    quantity: int
    position: str


class ProductUpdateDTO(BaseModel):
    id: Optional[int] = None
    description: str = None
    barcode: str
    price_per_unit: float = None
    note: str = None
    quantity: int = None
    position: str = None


class ProductCreateDTO(BaseModel):
    id: Optional[int] = None
    description: str
    barcode: str
    price_per_unit: float
    note: Optional[str] = ""
    quantity: Optional[int] = 0
    position: Optional[str] = ""
