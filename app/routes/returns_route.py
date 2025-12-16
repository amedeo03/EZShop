from typing import List

from fastapi import APIRouter, Depends, status

from app.config.config import ROUTES
from app.controllers.return_controller import ReturnController
from app.middleware.auth_middleware import authenticate_user
from app.models.DTO.boolean_response_dto import BooleanResponseDTO
from app.models.DTO.return_transaction_dto import ReturnTransactionDTO
from app.models.user_type import UserType

'''
ToDo:
1. Define DTO
2. Define DAO
3. Implement controller
4. Implement routes
'''

router = APIRouter(prefix=ROUTES["V1_RETURNS"], tags=["Returns"])
controller = ReturnController()

@router.post(
    "/",
    response_model=ReturnTransactionDTO,
    status_code=status.HTTP_201_CREATED,
    dependencies=[
        Depends(authenticate_user([UserType.Administrator, UserType.ShopManager, UserType.Cashier]))
    ],
)
async def create_return_transaction(sale_id: int) -> ReturnTransactionDTO:
    """
    Create a new empty return transaction.

    - Permissions: Administrator, ShopManager, Cashier
    - Request body: ReturnTransactionDTO
    - Returns: Created return transaction type as ReturnDTO
    - Status code: 201 Return Transaction created successfully
    """
    return await controller.create_return_transaction(sale_id=sale_id)


@router.get(
    "/",
    response_model=List[ReturnTransactionDTO],
    status_code=status.HTTP_200_OK,
    dependencies=[
        Depends(
            authenticate_user(
                [UserType.Administrator, UserType.ShopManager, UserType.Cashier]
            )
        )
    ],
)
async def list_returns() -> List[ReturnTransactionDTO]:
    """
    List present returns.

    - Permissions: Administrator, ShopManager, Cashier
    - Request body: no body required
    - Returns: list of ReturnTransactionDTO
    
    ToDO
    
    - Status code: 200 returns retrieved succesfully
    - Status code: 401 unauthenticated
    """

    return await controller.list_returns()

@router.get(
    "/{return_id}",
    response_model=ReturnTransactionDTO,
    status_code=status.HTTP_200_OK,
    dependencies=[
        Depends(
            authenticate_user(
                [UserType.Administrator, UserType.ShopManager, UserType.Cashier]
            )
        )
    ],
)
async def get_return_by_id(return_id: int) -> ReturnTransactionDTO:
    """
    return a return transaction given its ID.

    - Permissions: Administrator, ShopManager, Cashier
    - Request body: return_id as int
    - Returns: ReturnTransactionDTO
    
    TODO:
    
    - Status code: 200 return retrieved succesfully
    - Status code: 400 missing or invalid ID
    - Status code: 401 unauthenticated
    - Status code: 404 return not found
    """

    return await controller.get_return_by_id(return_id)

@router.delete(
    "/{return_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[
        Depends(
            authenticate_user(
                [UserType.Administrator, UserType.ShopManager, UserType.Cashier]
            )
        )
    ],
)
async def delete_return(return_id: int) -> None:
    """
    delete an existing not REIMBURSED return

    - Permissions: Administrator, ShopManager, Cashier
    - Request body: return_id as int
    - Returns: None
    
    TODO:
    
    - Status code: 204 return deleted succesfully
    - Status code: 400 Bad Request
    - Status code: 401 unauthenticated
    - Status code: 404 return or sale not found
    - Status code: 420 Cannot delete a Reimbursed return
    """
    await controller.delete_return(return_id)

    return

@router.get(
    "/sale/{sale_id}",
    response_model=List[ReturnTransactionDTO],
    status_code=status.HTTP_200_OK,
    dependencies=[
        Depends(
            authenticate_user(
                [UserType.Administrator, UserType.ShopManager, UserType.Cashier]
            )
        )
    ],
)
async def list_returns_for_sale_id(sale_id: int) -> List[ReturnTransactionDTO]:
    """
    Retrieves all return transactions associated with a sale.

    - Permissions: Administrator, ShopManager, Cashier
    - Request body: sale_id as int
    - Returns: List[ReturnTransactionDTO]
    
    TODO:
    
    - Status code: 200 return retrieved succesfully
    - Status code: 400 missing or invalid ID
    - Status code: 401 unauthenticated
    """

    return await controller.list_returns_for_sale_id(sale_id)

@router.post(
    "/{return_id}/items",
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
async def attach_product_to_return_transaction(return_id: int, barcode: str, amount: int) -> BooleanResponseDTO:
    """
    Add a product specified by barcode to a specific OPEN return transaction

    - Permissions: Administrator, ShopManager, Cashier
    - Request body: return_id as int, barcode as str, amount as int
    - Returns: BooleanResponseDTO
    
    - Status code: 201 product added succesfully
    - Status code: 400 invalid ID or insufficient stock
    - Status code: 401 unauthenticated
    - Status code: 404 sale or product not found
    - Status code: 420 Invalid sale state for return
    """

    return await controller.attach_product_to_return_transaction(return_id, barcode, amount)