from typing import List

from fastapi import APIRouter, Depends, status

from app.config.config import ROUTES
from app.controllers_instances import orders_controller, products_controller
from app.middleware.auth_middleware import authenticate_user
from app.models.DTO.boolean_response_dto import BooleanResponseDTO
from app.models.DTO.order_dto import OrderDTO
from app.models.user_type import UserType

router = APIRouter(prefix=ROUTES["V1_ORDERS"], tags=["orders"])
controller = orders_controller


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
    return await controller.create_order(order, products_controller)


@router.post(
    "/payfor",
    response_model=OrderDTO,
    status_code=status.HTTP_201_CREATED,
    dependencies=[
        Depends(authenticate_user([UserType.Administrator, UserType.ShopManager]))
    ],
)
async def pay_order_for(order: OrderDTO):
    """
    Create and pay an order for a product immediately.
    - Permissions: Administrator, ShopManager
    """
    return await controller.pay_order_for(order)


@router.get(
    "/",
    response_model=List[OrderDTO],
    status_code=status.HTTP_200_OK,
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


@router.patch(
    "/{order_id}/pay",
    response_model=BooleanResponseDTO,
    status_code=status.HTTP_201_CREATED,
    dependencies=[
        Depends(authenticate_user([UserType.Administrator, UserType.ShopManager]))
    ],
)
async def pay_order(order_id: int):
    """
    Pay for an existing issued order.
    - Permissions: Administrator, ShopManager
    """
    return await controller.pay_order(order_id)


@router.patch(
    "/{order_id}/arrival",
    response_model=BooleanResponseDTO,
    status_code=status.HTTP_201_CREATED,
    dependencies=[
        Depends(authenticate_user([UserType.Administrator, UserType.ShopManager]))
    ],
)
async def record_order_arrival(order_id: int):
    """
    Record the arrival of an order.
    Marks as COMPLETED and updates inventory.
    - Permissions: Administrator, ShopManager
    """
    return await controller.record_arrival(order_id)
