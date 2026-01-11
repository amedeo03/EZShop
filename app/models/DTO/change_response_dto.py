from pydantic import BaseModel


class ChangeResponseDTO(BaseModel):
    change: float
