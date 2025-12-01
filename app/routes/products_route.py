from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from app.models.DTO.product_dto import ProductTypeDTO
from app.models.user_type import UserType
from app.controllers.products_controller import ProductsController
from app.middleware.auth_middleware import authenticate_user
from app.config.config import ROUTES
from fastapi import Response
from app.models.errors.notfound_error import NotFoundError
from app.models.errors.bad_request import BadRequestError


router = APIRouter(prefix=ROUTES['V1_PRODUCTS'], tags=["Products"])
controller = ProductsController()

@router.post("/", 
    response_model= ProductTypeDTO,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(authenticate_user([UserType.Administrator, UserType.ShopManager]))])
async def create_product(product: ProductTypeDTO):
    """
    Create a new product.

    - Permissions: Administrator, ShopManager
    - Request body: ProductTypeDTO
    - Returns: Created product type as ProductTypeDTO
    - Raises:
      - BadRequestError: productCode less than 12-14 digits. When mandatory fields (description, pricePerUnit) are missing or invalid
    - Status code: 201 Product created successfully
    """

    if product.description is None or product.description == '':
        raise BadRequestError('description is a mandatory field')
    if product.pricePerUnit is None or product.pricePerUnit == '':
        raise BadRequestError('pricePerUnit type is a mandatory field')
    if len(product.productCode) < 12 or len(product.productCode) > 14:
        raise BadRequestError('productCode must be a string of 12-14 digits')
    return await controller.create_product(product)


@router.get("/", response_model=List[ProductTypeDTO], dependencies=[Depends(authenticate_user([UserType.Administrator, UserType.ShopManager, UserType.Cashier]))])
async def list_products():
    """
    List of all products.

    - Permissions: Administrator, ShopManager, Cashier
    - Returns: List of ProductTypeDTO
    - Status code: 200 OK
    """
    return await controller.list_products()

@router.get("/{product_id}", response_model=ProductTypeDTO, dependencies=[Depends(authenticate_user([UserType.Administrator, UserType.ShopManager, UserType.Cashier]))])
async def get_product(product_id: int):
    """
    Retrieve a single product by ID.

    - Permissions: Administrator, ShopManager, Cashier
    - Path parameter: product_id (int)
    - Returns: ProductDTO for the requested product
    - Raises:
      - NotFoundError: when the product id doesn't exist
    - Status code: 200 OK
    """
    product = await controller.get_product(product_id)
    if not product:
        raise NotFoundError("Product not found")
    return product

@router.get("/barcode/{barcode}", response_model=ProductTypeDTO, dependencies=[Depends(authenticate_user([UserType.Administrator, UserType.ShopManager]))])
async def get_product_by_barcode(barcode: str):
    """
    Retrieve a single product by barcode.

    - Permissions: Administrator, ShopManager
    - Path parameter: barcode (str)
    - Returns: ProductDTO for the requested product
    - Raises:
      - NotFoundError: when the product id doesn't exist
      - InvalidFormatError: when barcode format is invalid
    - Status code: 200 OK
    """
    if len(barcode) < 12 or len(barcode) > 14:
        raise BadRequestError('barcode must be a string of 12-14 digits')

    product = await controller.get_product_by_barcode(barcode)
    if not product:
        raise NotFoundError("Product not found")
    return product
