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
    - Status code: 201 Created
    """
    if product.description is None or product.description == '':
        raise BadRequestError('Description is a mandatory field')
    if product.pricePerUnit is None or product.pricePerUnit == '':
        raise BadRequestError('pricePerUnit type is a mandatory field')
    if len(product.productCode) < 12 and len(product.productCode) > 14:
        raise BadRequestError('productCode must be a string of 12-14 digits')
    return await controller.create_product(product)


@router.get("/", response_model=List[ProductTypeDTO], dependencies=[Depends(authenticate_user([UserType.Administrator, UserType.ShopManager, UserType.Cashier]))])
async def list_products():
    """
    List all products.

    - Permissions: Administrator, ShopManager, Cashier
    - Returns: List of ProductTypeDTO
    - Status code: 200 OK
    """
    return await controller.list_products()


# @router.get("/{user_id}", response_model=UserResponseDTO,
#             dependencies=[Depends(authenticate_user([UserType.Administrator]))])
# async def get_user(user_id: int):
#     """
#     Retrieve a single user by ID.

#     - Permissions: Administrator
#     - Path parameter: user_id (int)
#     - Returns: UserResponseDTO for the requested user
#     - Raises:
#       - NotFoundError: when the user does not exist
#     - Status code: 200 OK
#     """
#     user = await controller.get_user(user_id)
#     if not user:
#         raise NotFoundError("User not found")
#     return user


# @router.put("/{user_id}", response_model=UserResponseDTO, 
#     status_code=status.HTTP_201_CREATED,
#     dependencies=[Depends(authenticate_user([UserType.Administrator]))])
# async def update_user(user_id: int, user: UserDTO):
#     """
#     Update an existing user.

#     - Permissions: Administrator
#     - Path parameter: user_id (int)
#     - Request body: UserDTO (fields to update)
#     - Returns: Updated user as UserResponseDTO
#     - Raises:
#       - NotFoundError: when the user to update does not exist
#     - Status code: 201 Created
#     """
#     updated = await controller.update_user(user_id, user)
#     if not updated:
#         raise NotFoundError("User not found")
#     return updated


# @router.delete("/{user_id}", 
#                status_code=status.HTTP_204_NO_CONTENT, 
#                dependencies=[Depends(authenticate_user([UserType.Administrator]))])
# async def delete_user(user_id: int):
#     """
#     Delete a user by ID.

#     - Permissions: Administrator
#     - Path parameter: user_id (int)
#     - Returns: No content (204) on success
#     - Raises:
#       - NotFoundError: when the user to delete does not exist
#     - Status code: 204 No Content
#     """
#     success = await controller.delete_user(user_id)
#     if not success:
#         raise NotFoundError("User not found")
#     return Response(status_code=status.HTTP_204_NO_CONTENT)