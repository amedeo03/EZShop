from pydantic import BaseModel


class RefundResponseDTO(BaseModel):
    refund_amount: float