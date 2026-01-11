from fastapi import APIRouter, Depends, Response, status

from app.config.config import ROUTES
from app.controllers_instances import accounting_controller
from app.middleware.auth_middleware import authenticate_user
from app.models.DTO.boolean_response_dto import BooleanResponseDTO
from app.models.user_type import UserType

router = APIRouter(prefix=ROUTES["V1_ACCOUNTING"], tags=["Accounting"])

controller = accounting_controller


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(authenticate_user([UserType.Administrator]))],
)
async def get_current_balance():
    return {"balance": await controller.get_balance()}


@router.post(
    "/set",
    status_code=status.HTTP_201_CREATED,
    response_model=BooleanResponseDTO,
    dependencies=[Depends(authenticate_user([UserType.Administrator]))],
)
async def set_balance(amount: float):
    """
    Set the system balance to a specific amount.
    - Permissions: Administrator
    - Query Param: amount (float)
    """
    return await controller.set_balance(amount)


@router.post(
    "/reset",
    status_code=status.HTTP_205_RESET_CONTENT,
    dependencies=[Depends(authenticate_user([UserType.Administrator]))],
)
async def reset_balance() -> None:
    """
    Reset the system balance to zero.
    - Permissions: Administrator
    """
    await controller.reset_balance()
    return Response(status_code=status.HTTP_205_RESET_CONTENT)
