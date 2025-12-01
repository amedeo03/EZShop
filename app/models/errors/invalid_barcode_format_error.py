from app.models.errors.app_error import AppError

class InvalidFormatError(AppError):
    """Invalid format error (400)"""

    def __init__(self, message: str):
        super().__init__(message, 400)
        self.name = "InvalidFormatError"
