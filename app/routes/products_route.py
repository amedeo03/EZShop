from typing import List

from fastapi import APIRouter, Depends, Response, status

from app.config.config import ROUTES
from app.controllers_instances import (
    orders_controller,
    products_controller,
    returned_products_controller,
    sold_products_controller,
)
from app.middleware.auth_middleware import authenticate_user
from app.models.DTO.boolean_response_dto import BooleanResponseDTO
from app.models.DTO.product_dto import (
    ProductCreateDTO,
    ProductTypeDTO,
    ProductUpdateDTO,
)
from app.models.user_type import UserType

router = APIRouter(prefix=ROUTES["V1_PRODUCTS"], tags=["Products"])
controller = products_controller


@router.post(
    "/",
    response_model=ProductTypeDTO,
    status_code=status.HTTP_201_CREATED,
    dependencies=[
        Depends(authenticate_user([UserType.Administrator, UserType.ShopManager]))
    ],
)
async def create_product(product: ProductCreateDTO):
    """
    Create a new product.

    - Permissions: Administrator, ShopManager
    - Request body: ProductCreateDTO
    - Returns: Created product type as ProductCreateDTO
    - Status code: 201 Product created successfully
    """
    return await controller.create_product(product)


@router.get(
    "/",
    response_model=List[ProductTypeDTO],
    dependencies=[
        Depends(
            authenticate_user(
                [UserType.Administrator, UserType.ShopManager, UserType.Cashier]
            )
        )
    ],
)
async def list_products():
    """
    List of all products.

    - Permissions: Administrator, ShopManager, Cashier
    - Returns: List of ProductTypeDTO
    - Status code: 200 OK
    """
    return await controller.list_products()


@router.get(
    "/search",
    response_model=List[ProductTypeDTO],
    dependencies=[
        Depends(authenticate_user([UserType.Administrator, UserType.ShopManager]))
    ],
)
async def get_product_by_description(query: str):
    """
    Retrieve a single product by description.
    - Permissions: Administrator, ShopManager
    - Query parameter: query (str)
    - Returns: ProductDTO for the products with 'query' as substring in 'description'
    - Status code: 200 OK
    """
    return await controller.get_product_by_description(query)


@router.get(
    "/{product_id}",
    response_model=ProductTypeDTO,
    dependencies=[
        Depends(
            authenticate_user(
                [UserType.Administrator, UserType.ShopManager, UserType.Cashier]
            )
        )
    ],
)
async def get_product(product_id: int):
    """
    Retrieve a single product by ID.

    - Permissions: Administrator, ShopManager, Cashier
    - Path parameter: product_id (int)
    - Returns: ProductDTO for the requested product
    - Status code: 200 OK
    """
    return await controller.get_product(product_id)


@router.get(
    "/barcode/{barcode}",
    response_model=ProductTypeDTO,
    dependencies=[
        Depends(authenticate_user([UserType.Administrator, UserType.ShopManager]))
    ],
)
async def get_product_by_barcode(barcode: str):
    """
    Retrieve a single product by barcode.

    - Permissions: Administrator, ShopManager
    - Path parameter: barcode (str)
    - Returns: ProductDTO for the requested product
    - Status code: 200 OK
    """
    return await controller.get_product_by_barcode(barcode)


@router.put(
    "/{product_id}",
    response_model=BooleanResponseDTO,
    status_code=status.HTTP_200_OK,
    dependencies=[
        Depends(authenticate_user([UserType.Administrator, UserType.ShopManager]))
    ],
)
async def update_product(product_id: int, product: ProductUpdateDTO):
    """
    Update an existing product.
    - Permissions: Administrator, ShopManager
    - Path parameter: id (int)
    - Request body: ProductTypeDTO (fields to update)
    - Returns: Updated user as ProductTypeDTO
    - Status code: 200 OK
    """
    return await controller.update_product(
        product_id=product_id,
        product_dto=product,
        sold_products_controller=sold_products_controller,
        orders_controller=orders_controller,
        returned_products_controller=returned_products_controller,
    )


@router.delete(
    "/{product_id}",
    # response_model=BooleanResponseDTO,
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[
        Depends(authenticate_user([UserType.Administrator, UserType.ShopManager]))
    ],
)
async def delete_product(product_id: int) -> None:
    """
    Delete an existing product.
    - Permissions: Administrator, ShopManager
    - Path parameter: id (int)
    - Returns: None
    - Status code: 204 No Content
    """
    await controller.delete_product(
        product_id=product_id,
        sold_products_controller=sold_products_controller,
        orders_controller=orders_controller,
        returned_products_controller=returned_products_controller,
    )

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.patch(
    "/{product_id}/position",
    response_model=BooleanResponseDTO,
    status_code=status.HTTP_201_CREATED,
    dependencies=[
        Depends(authenticate_user([UserType.Administrator, UserType.ShopManager]))
    ],
)
async def update_product_position(product_id: int, position: str) -> BooleanResponseDTO:
    """
    Update an existing position of a product.
    - Permissions: Administrator, ShopManager
    - Path parameter: id (int)
    - Query parameter: position (str)
    - Returns: Result of the operation as BooleanResponseDTO
    - Status code: 201 Updated
    """
    return await controller.update_product_position(product_id, position)


@router.patch(
    "/{product_id}/quantity",
    response_model=BooleanResponseDTO,
    status_code=status.HTTP_201_CREATED,
    dependencies=[
        Depends(authenticate_user([UserType.Administrator, UserType.ShopManager]))
    ],
)
async def update_product_quantity(product_id: int, quantity: int) -> BooleanResponseDTO:
    """
    Update an existing quantity of a product.
    - Permissions: Administrator, ShopManager
    - Path parameter: id (int)
    - Query parameter: quantity (int)
    - Returns: Result of the operation as BooleanResponseDTO
    - Status code: 200 OK
    """
    return await controller.update_product_quantity(product_id, quantity)
