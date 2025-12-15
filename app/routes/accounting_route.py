from fastapi import APIRouter, Depends, status
from pydantic import BaseModel

from app.config.config import ROUTES
from app.controllers.accounting_controller import AccountingController
from app.middleware.auth_middleware import authenticate_user
from app.models.DTO.boolean_response_dto import BooleanResponseDTO
from app.models.user_type import UserType
from app.repositories.accounting_repository import AccountingRepository

# Apply the Auth Middleware to the entire router ---
# This locks every endpoint in this file to Administrators only.
router = APIRouter(
    prefix=ROUTES["V1_ACCOUNTING"],
    tags=["Accounting"],
    dependencies=[Depends(authenticate_user([UserType.Administrator]))],
)


class BalanceRequest(BaseModel):
    amount: float


def get_controller():
    repo = AccountingRepository()
    return AccountingController()


@router.get("", status_code=status.HTTP_200_OK)
async def get_current_balance(
    controller: AccountingController = Depends(get_controller),
):
    return {"balance": await controller.get_balance()}


@router.post("/set", status_code=status.HTTP_201_CREATED)
async def set_balance(
    amount: float,
    controller: AccountingController = Depends(get_controller),
):
    """
    Set the system balance to a specific amount.
    - Permissions: Administrator
    - Query Param: amount (float)
    """
    new_bal = await controller.set_balance(amount)

    return BooleanResponseDTO(
        success=True,
    )


@router.post("/reset", status_code=status.HTTP_205_RESET_CONTENT)
async def reset_balance(controller: AccountingController = Depends(get_controller)):
    """
    Reset the system balance to zero.
    - Permissions: Administrator
    """
    new_bal = await controller.reset_balance()
    return {"message": "Balance reset", "balance": new_bal}
