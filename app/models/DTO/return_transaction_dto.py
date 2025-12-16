from typing import Optional, List

from pydantic import BaseModel
from return_status_type import ReturnStatus
from ezshop.app.models.DTO.returned_item_dto import ReturnedItemDTO
from datetime import datetime


class ReturnTransactionDTO(BaseModel):
    id: Optional[int] = None
    sale_id: int = None
    status: ReturnStatus = None
    created_at: datetime = None
    closed_at: Optional[datetime] = None
    lines: List[ReturnedItemDTO] = []

