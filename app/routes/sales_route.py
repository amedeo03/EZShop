from typing import List

from fastapi import APIRouter, Depends, status

from app.config.config import ROUTES
from app.controllers.sales_controller import SalesController
from app.middleware.auth_middleware import authenticate_user
from app.models.DTO.boolean_response_dto import BooleanResponseDTO
from app.models.DTO.sale_dto import SaleDTO
from app.models.user_type import UserType
from app.routes.products_route import get_product_by_barcode

router = APIRouter(prefix=ROUTES["V1_SALES"], tags=["Sales"])
controller = SalesController()


@router.post(
    "/",
    response_model=SaleDTO,
    status_code=status.HTTP_201_CREATED,
    dependencies=[
        Depends(
            authenticate_user(
                [UserType.Administrator, UserType.ShopManager, UserType.Cashier]
            )
        )
    ],
)
async def create_sale():
    """
    Create a new empty sale.

    - Permissions: Administrator, ShopManager, Cashier
    - Request body: no body required
    - Returns: Empty sale as SaleDTO
    - Status code: 201 Product created successfully
    - Status code: 401 anauthenticated
    """

    return await controller.create_sale()


@router.get(
    "/",
    response_model=List[SaleDTO],
    status_code=status.HTTP_200_OK,
    dependencies=[
        Depends(
            authenticate_user(
                [UserType.Administrator, UserType.ShopManager, UserType.Cashier]
            )
        )
    ],
)
async def list_sales():
    """
    List present sales.

    - Permissions: Administrator, ShopManager, Cashier
    - Request body: no body required
    - Returns: list of SaleDTO
    - Status code: 200 sales retrieved succesfully
    - Status code: 401 anauthenticated
    """

    return await controller.list_sales()


@router.get(
    "/{sale_id}",
    response_model=SaleDTO,
    status_code=status.HTTP_200_OK,
    dependencies=[
        Depends(
            authenticate_user(
                [UserType.Administrator, UserType.ShopManager, UserType.Cashier]
            )
        )
    ],
)
async def get_sale_by_id(sale_id: int):
    """
    return a sale given its ID.

    - Permissions: Administrator, ShopManager, Cashier
    - Request body: sale_id as int
    - Returns: SaleDTO
    - Status code: 200 sale retrieved succesfully
    - Status code: 400 missing or invalid ID
    - Status code: 401 anauthenticated
    - Status code: 404 sale not found
    """

    return await controller.get_sale_by_id(sale_id)


@router.post(
    "/{sale_id}/items",
    response_model=BooleanResponseDTO,
    status_code=status.HTTP_201_CREATED,
    dependencies=[
        Depends(
            authenticate_user(
                [UserType.Administrator, UserType.ShopManager, UserType.Cashier]
            )
        )
    ],
)
async def attach_product(sale_id: int, barcode: str, amount: int):
    """
    Add a product specified by barcode to a specific OPEN sale

    - Permissions: Administrator, ShopManager, Cashier
    - Request body: sale_id as int, barcode as str, amount as int
    - Returns: BooleanResponseDTO
    - Status code: 201 product added succesfully
    - Status code: 400 invalid ID or insufficient stock
    - Status code: 401 anauthenticated
    - Status code: 404 sale or product not found
    - Status code: 410 invalid sale status
    """

    return await controller.attach_product(sale_id, barcode, amount)


@router.delete(
    "/{sale_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[
        Depends(
            authenticate_user(
                [UserType.Administrator, UserType.ShopManager, UserType.Cashier]
            )
        )
    ],
)
async def delete_sale(sale_id: int) -> None:
    """
    Add a product specified by barcode to a specific OPEN sale

    - Permissions: Administrator, ShopManager, Cashier
    - Request body: sale_id as int
    - Returns: BooleanResponseDTO
    - Status code: 204 sale deleted succesfully
    - Status code: 400 invalid ID or sale cannot be deleted
    - Status code: 401 anauthenticated
    - Status code: 404 sale or product not found
    """
    await controller.delete_sale(sale_id)

    return
