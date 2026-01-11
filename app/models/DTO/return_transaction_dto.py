from typing import Optional, List

from pydantic import BaseModel, ConfigDict
from app.models.return_status_type import ReturnStatus
from app.models.DTO.returned_product_dto import ReturnedProductDTO
from datetime import datetime


class ReturnTransactionDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True) 
    
    id: Optional[int] = None
    sale_id: int = None
    status: ReturnStatus = None
    created_at: datetime = None
    closed_at: Optional[datetime] = None
    lines: List[ReturnedProductDTO] = []

