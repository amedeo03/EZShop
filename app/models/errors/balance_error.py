from fastapi.responses import JSONResponse
from app.models.errors.app_error import AppError

class BalanceError(AppError):
    def __init__(self, message: str):
        super().__init__(message, status_code=421)
        self.name = "BalanceError"