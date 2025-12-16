from app.models.errors.app_error import AppError


class InsufficientQuantitySoldError(AppError):
    """Invalid sale status (400)"""

    def __init__(self, message: str):
        super().__init__(message, 400)
        self.name = "InsufficientQuantitySoldError"