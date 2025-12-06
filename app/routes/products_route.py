from typing import List

from fastapi import APIRouter, Depends, status

from app.config.config import ROUTES
from app.controllers.products_controller import ProductsController
from app.middleware.auth_middleware import authenticate_user
from app.models.DTO.boolean_response_dto import BooleanResponseDTO
from app.models.DTO.product_dto import ProductTypeDTO
from app.models.user_type import UserType

router = APIRouter(prefix=ROUTES["V1_PRODUCTS"], tags=["Products"])
controller = ProductsController()


@router.post(
    "/",
    response_model=ProductTypeDTO,
    status_code=status.HTTP_201_CREATED,
    dependencies=[
        Depends(authenticate_user([UserType.Administrator, UserType.ShopManager]))
    ],
)
async def create_product(product: ProductTypeDTO):
    """
    Create a new product.

    - Permissions: Administrator, ShopManager
    - Request body: ProductTypeDTO
    - Returns: Created product type as ProductTypeDTO
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
async def get_product(product_id: int | str):
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
async def update_product(product_id: int, product: ProductTypeDTO):
    """
    Update an existing product.
    - Permissions: Administrator, ShopManager
    - Path parameter: id (int)
    - Request body: ProductTypeDTO (fields to update)
    - Returns: Updated user as ProductTypeDTO
    - Status code: 200 OK
    """
    return await controller.update_product(product_id, product)
