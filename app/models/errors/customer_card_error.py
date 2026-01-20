from app.models.errors.app_error import AppError

class CustomerCardError(AppError):
    """Conflict error (400)"""
    
    def __init__(self, message: str):
        super().__init__(message, 500)
        self.name = "CustomerCardError"