from fastapi.responses import JSONResponse

class BalanceError(Exception):
    def __init__(self, message: str):
        self.message = message
        self.code = 421
        self.name = "BalanceError"

    def response(self):
        return JSONResponse(
            status_code=self.code,
            content={"code": self.code, "message": self.message, "name": self.name},
        )