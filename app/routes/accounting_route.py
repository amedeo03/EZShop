from fastapi import APIRouter, Depends, status, Response

from app.controllers.accounting_controller import AccountingController
from app.config.config import ROUTES

from app.middleware.auth_middleware import authenticate_user
from app.models.user_type import UserType
from app.models.DTO.boolean_response_dto import BooleanResponseDTO


router = APIRouter(
    prefix=ROUTES["V1_ACCOUNTING"], 
    tags=["Accounting"],
    dependencies=[
        Depends(authenticate_user([UserType.Administrator]))
    ]
)

controller = AccountingController()

@router.get("", status_code=status.HTTP_200_OK)
async def get_current_balance():
    return {"balance": await controller.get_balance()}

@router.post("/set", status_code=status.HTTP_201_CREATED)
async def set_balance(amount: float):
    """
    Set the system balance to a specific amount.
    - Permissions: Administrator
    - Query Param: amount (float)
    """
    await controller.set_balance(amount)
    
    return BooleanResponseDTO(success=True)

@router.post("/reset", status_code=status.HTTP_205_RESET_CONTENT)
async def reset_balance():
    """
    Reset the system balance to zero.
    - Permissions: Administrator
    """
    await controller.reset_balance()
    return Response(status_code=status.HTTP_205_RESET_CONTENT)