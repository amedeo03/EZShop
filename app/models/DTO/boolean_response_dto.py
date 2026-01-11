from pydantic import BaseModel


class BooleanResponseDTO(BaseModel):
    success: bool
