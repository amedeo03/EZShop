from typing import List

from fastapi import APIRouter, Depends, status

from app.config.config import ROUTES
from app.controllers_instances import (
    products_controller,
    sales_controller,
    sold_products_controller,
)
from app.middleware.auth_middleware import authenticate_user
from app.models.DTO.boolean_response_dto import BooleanResponseDTO
from app.models.DTO.change_response_dto import ChangeResponseDTO
from app.models.DTO.points_response_dto import PointsResponseDTO
from app.models.DTO.sale_dto import SaleDTO
from app.models.user_type import UserType

router = APIRouter(prefix=ROUTES["V1_SALES"], tags=["Sales"])
controller = sales_controller


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
async def create_sale() -> SaleDTO:
    """
    Create a new empty sale.

    - Permissions: Administrator, ShopManager, Cashier
    - Request body: no body required
    - Returns: Empty sale as SaleDTO
    - Status code: 201 Product created successfully
    - Status code: 401 unauthenticated
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
async def list_sales() -> List[SaleDTO]:
    """
    List present sales.

    - Permissions: Administrator, ShopManager, Cashier
    - Request body: no body required
    - Returns: list of SaleDTO
    - Status code: 200 sales retrieved succesfully
    - Status code: 401 unauthenticated
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
async def get_sale_by_id(sale_id: int) -> SaleDTO:
    """
    return a sale given its ID.

    - Permissions: Administrator, ShopManager, Cashier
    - Request body: sale_id as int
    - Returns: SaleDTO
    - Status code: 200 sale retrieved succesfully
    - Status code: 400 missing or invalid ID
    - Status code: 401 unauthenticated
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
async def attach_product(sale_id: int, barcode: str, amount: int) -> BooleanResponseDTO:
    """
    Add a product specified by barcode to a specific OPEN sale

    - Permissions: Administrator, ShopManager, Cashier
    - Request body: sale_id as int, barcode as str, amount as int
    - Returns: BooleanResponseDTO
    - Status code: 201 product added succesfully
    - Status code: 400 invalid ID or insufficient stock
    - Status code: 401 unauthenticated
    - Status code: 404 sale or product not found
    - Status code: 410 invalid sale status
    """

    return await controller.attach_product(
        sale_id,
        barcode,
        amount,
        products_controller=products_controller,
        sold_products_controller=sold_products_controller,
    )


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
    delete an existing not PAID sale

    - Permissions: Administrator, ShopManager, Cashier
    - Request body: sale_id as int
    - Returns: None
    - Status code: 204 sale deleted succesfully
    - Status code: 400 invalid ID or sale cannot be deleted
    - Status code: 401 unauthenticated
    - Status code: 404 sale or product not found
    """
    await controller.delete_sale(
        sale_id, sold_products_controller=sold_products_controller
    )


@router.delete(
    "/{sale_id}/items",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=BooleanResponseDTO,
    dependencies=[
        Depends(
            authenticate_user(
                [UserType.Administrator, UserType.ShopManager, UserType.Cashier]
            )
        )
    ],
)
async def edit_product_quantity(
    sale_id: int, barcode: str, amount: int
) -> BooleanResponseDTO:
    """
    delete a product from an OPEN sale

    - Permissions: Administrator, ShopManager, Cashier
    - Request body: sale_id as int
    - Returns: BooleanResponseDTO
    - Status code: 202 product removed succesfully
    - Status code: 400 invalid ID or quantity
    - Status code: 401 unauthenticated
    - Status code: 404 sale or product not found
    - Status code: 420 invalid sale status
    """

    return await controller.edit_sold_product_quantity(
        sale_id, barcode, amount, sold_products_controller=sold_products_controller
    )


@router.patch(
    "/{sale_id}/discount",
    response_model=BooleanResponseDTO,
    status_code=status.HTTP_200_OK,
    dependencies=[
        Depends(
            authenticate_user(
                [UserType.Administrator, UserType.ShopManager, UserType.Cashier]
            )
        )
    ],
)
async def edit_sale_discount(sale_id: int, discount_rate: float) -> BooleanResponseDTO:
    """
    change discount_rate field of an OPEN sale

    - Permissions: Administrator, ShopManager, Cashier
    - Request body: sale_id as int, discount_rate as float
    - Returns: BooleanResponseDTO
    - Status code: 200 sale patched succesfully
    - Status code: 400 invalid ID or discount_rate
    - Status code: 401 unauthenticated
    - Status code: 404 sale not found
    - Status code: 420 invalid sale status
    """
    return await controller.edit_sale_discount(sale_id, discount_rate)


@router.patch(
    "/{sale_id}/items/{product_barcode}/discount",
    response_model=BooleanResponseDTO,
    status_code=status.HTTP_200_OK,
    dependencies=[
        Depends(
            authenticate_user(
                [UserType.Administrator, UserType.ShopManager, UserType.Cashier]
            )
        )
    ],
)
async def edit_product_discount(
    sale_id: int, product_barcode: str, discount_rate: float
) -> BooleanResponseDTO:
    """
    change discount_rate field of a product in an OPEN sale

    - Permissions: Administrator, ShopManager, Cashier
    - Request body: sale_id as int, discount_rate as float, product barcode as str
    - Returns: BooleanResponseDTO
    - Status code: 200 product patched succesfully
    - Status code: 400 invalid ID or discount_rate
    - Status code: 401 unauthenticated
    - Status code: 404 sale not found
    - Status code: 420 invalid sale status
    """
    return await controller.edit_product_discount(
        sale_id,
        product_barcode,
        discount_rate,
        sold_products_controller=sold_products_controller,
    )


@router.patch(
    "/{sale_id}/close",
    response_model=BooleanResponseDTO,
    status_code=status.HTTP_200_OK,
    dependencies=[
        Depends(
            authenticate_user(
                [UserType.Administrator, UserType.ShopManager, UserType.Cashier]
            )
        )
    ],
)
async def close_sale(sale_id: int) -> BooleanResponseDTO:
    """
    Turn an OPEN sale status to PENDING.
    It will instead delete the sale if there are no products registered to the sale

    - Permissions: Administrator, ShopManager, Cashier
    - Request body: sale_id as int
    - Returns: BooleanResponseDTO
    - Status code: 200 sale closed succesfully
    - Status code: 400 invalid id
    - Status code: 401 unauthenticated
    - Status code: 404 sale not found
    - Status code: 420 sale already closed
    """
    return await controller.close_sale(sale_id)


@router.patch(
    "/{sale_id}/pay",
    response_model=ChangeResponseDTO,
    status_code=status.HTTP_200_OK,
    dependencies=[
        Depends(
            authenticate_user(
                [UserType.Administrator, UserType.ShopManager, UserType.Cashier]
            )
        )
    ],
)
async def pay_sale(sale_id: int, cash_amount: float) -> ChangeResponseDTO:
    """
    Pay an existing PENDING sale with cash, then marks the sale as PAID and returns the change needed

    - Permissions: Administrator, ShopManager, Cashier
    - Request body: sale_id as int
    - Returns: ChangeResponseDTO
    - Status code: 200 sale paid succesfully
    - Status code: 400 invalid id
    - Status code: 401 unauthenticated
    - Status code: 404 sale not found
    - Status code: 420 sale not pending
    """
    return await controller.pay_sale(sale_id, cash_amount)


@router.get(
    "/{sale_id}/points",
    response_model=PointsResponseDTO,
    status_code=status.HTTP_200_OK,
    dependencies=[
        Depends(
            authenticate_user(
                [UserType.Administrator, UserType.ShopManager, UserType.Cashier]
            )
        )
    ],
)
async def get_sale_points(sale_id: int) -> PointsResponseDTO:
    """
    Compute fidelity points earned after paying a sale

    - Permissions: Administrator, ShopManager, Cashier
    - Request body: sale_id as int
    - Returns: PointsResponseDTO
    - Status code: 200 points computed succesfully
    - Status code: 400 invalid id
    - Status code: 401 unauthenticated
    - Status code: 404 sale not found
    - Status code: 420 sale must be PAID before computing points
    """
    return await controller.get_points(sale_id)
