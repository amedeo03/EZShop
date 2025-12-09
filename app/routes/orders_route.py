from typing import List

from fastapi import APIRouter, Depends, status

from app.config.config import ROUTES
from app.controllers.orders_controller import OrdersController
from app.middleware.auth_middleware import authenticate_user
from app.models.DTO.order_dto import OrderDTO
from app.models.user_type import UserType


router = APIRouter(prefix=ROUTES["V1_ORDERS"], tags=["orders"])
controller = OrdersController()

@router.post(
    "/",
    response_model=OrderDTO,
    status_code=status.HTTP_201_CREATED,
    dependencies=[
        Depends(authenticate_user([UserType.Administrator, UserType.ShopManager]))
    ],
)
async def issue_order(order: OrderDTO):
    """
    Issue a new order.
    - Permissions: Administrator, ShopManager
    """
    return await controller.create_order(order)

@router.get(
    "/",
    response_model=List[OrderDTO],
    dependencies=[
        Depends(authenticate_user([UserType.Administrator, UserType.ShopManager]))
    ],
)
async def list_orders():
    """
    List all orders.
    - Permissions: Administrator, ShopManager
    """
    return await controller.list_orders()