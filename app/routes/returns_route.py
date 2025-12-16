from typing import List

from fastapi import APIRouter, Depends, status

from app.config.config import ROUTES
from app.controllers.return_controller import ReturnController
from app.middleware.auth_middleware import authenticate_user
from app.models.DTO.boolean_response_dto import BooleanResponseDTO
from ezshop.app.models.DTO.return_transaction_dto import ReturnTransactionDTO
from app.models.user_type import UserType

'''
ToDo:
1. Define DTO
2. Define DAO
3. Implement controller
4. Implement routes
'''

router = APIRouter(prefix=ROUTES["V1_PRODUCTS"], tags=["Products"])
controller = ReturnController()

@router.post(
    "/",
    response_model=ReturnTransactionDTO,
    status_code=status.HTTP_201_CREATED,
    dependencies=[
        Depends(authenticate_user([UserType.Administrator, UserType.ShopManager, UserType.Cashier]))
    ],
)
async def create_return_transaction(return_transaction: ReturnTransactionDTO):
    """
    Create a new return transaction.

    - Permissions: Administrator, ShopManager, Cashier
    - Request body: ReturnDTO
    - Returns: Created return transaction type as ReturnDTO
    - Status code: 201 Return Transaction created successfully
    """
    return await controller.create_return_transaction(return_transaction)