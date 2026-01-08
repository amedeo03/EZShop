from typing import List

from fastapi import APIRouter, Depends, status

from app.config.config import ROUTES
from app.controllers_instances import customer_controller
from app.middleware.auth_middleware import authenticate_user
from app.models.DTO.card_dto import CardResponseDTO
from app.models.DTO.customer_dto import (
    CustomerCreateDTO,
    CustomerResponseDTO,
    CustomerUpdateDTO,
)
from app.models.errors.bad_request import BadRequestError
from app.models.errors.notfound_error import NotFoundError
from app.models.user_type import UserType

router = APIRouter(prefix=ROUTES["V1_CUSTOMERS"], tags=["Customers"])
controller = customer_controller


@router.post(
    "/",
    response_model=CustomerResponseDTO,
    status_code=status.HTTP_201_CREATED,
    dependencies=[
        Depends(
            authenticate_user(
                [UserType.Administrator, UserType.Cashier, UserType.ShopManager]
            )
        )
    ],
)
async def create_customer(customer: CustomerCreateDTO):
    """
    Create a new custormer.

    - Permissions: all
    - Request body: CustomerCreateDTO (contains name)
    - Returns: Created Customer as CustomerResponseDTO
    - Status code: 201 Created
    """
    return await controller.create_customer(customer)


@router.get(
    "/",
    response_model=List[CustomerResponseDTO],
    dependencies=[
        Depends(
            authenticate_user(
                [UserType.Administrator, UserType.Cashier, UserType.ShopManager]
            )
        )
    ],
)
async def list_customer():
    """
    List all customer.

    - Permissions: all
    - Returns: List of CustomerResponseDTO
    - Status code: 200 OK
    """
    return await controller.list_customer()


@router.get(
    "/{customer_id}",
    response_model=CustomerResponseDTO,
    dependencies=[
        Depends(
            authenticate_user(
                [UserType.Administrator, UserType.Cashier, UserType.ShopManager]
            )
        )
    ],
)
async def get_customer(customer_id: str):
    """
    Retrieve a single customer by ID.

    - Permissions: all
    - Path parameter: customer_id (int)
    - Returns: CustomerResponseDTO for the requested customer
    - Raises:
      - NotFoundError: when the customer does not exist
      -BadRequestError: when customer_id format is not valid
    - Status code: 200 OK
    """
    customer = await controller.get_customer(customer_id)
    return customer


@router.put(
    "/{customer_id}",
    response_model=CustomerResponseDTO,
    status_code=status.HTTP_201_CREATED,
    dependencies=[
        Depends(
            authenticate_user(
                [UserType.Administrator, UserType.Cashier, UserType.ShopManager]
            )
        )
    ],
)
async def update_customer(customer_id: str, customer: CustomerUpdateDTO):
    """
    Update an existing customer.

    - Permissions: all
    - Path parameter: customer_id (int)
    - Request body: CustomerUpdateDTO (fields to update)
    - Returns: Updated customer as CustomerResponseDTO
    - Raises:
      - NotFoundError: when the customer to update does not exist
      -ConflictError: when a card is attached an other customer
    - Status code: 201 Created
    """
    updated = await controller.update_customer(customer_id, customer)
    
    return updated


@router.delete(
    "/{customer_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[
        Depends(
            authenticate_user(
                [UserType.Administrator, UserType.Cashier, UserType.ShopManager]
            )
        )
    ],
)
async def delete_customer(customer_id: str):
    """
    Delete a customer by ID.

    - Permissions: all
    - Path parameter: customer_id (int)
    - Returns: No content (204) on success
    - Raises:
      - NotFoundError: when the customer to delete does not exist
    - Status code: 204 No Content
    """
    success = await controller.delete_customer(customer_id)
    return success


# card
@router.post(
    "/cards",
    response_model=CardResponseDTO,
    status_code=status.HTTP_201_CREATED,
    dependencies=[
        Depends(
            authenticate_user(
                [UserType.Administrator, UserType.Cashier, UserType.ShopManager]
            )
        )
    ],
)
async def create_card():
    """
    Create a new custormer.

    - Permissions: all
    - Request body: CustomerCreateDTO (contains name, card)
    - Returns: Created Customer as CustomerResponseDTO
    - Status code: 201 Created
    """
    return await controller.create_card()


@router.patch(
    "/{customer_id}/attach-card/{card_id}",
    status_code=status.HTTP_201_CREATED,
    dependencies=[
        Depends(
            authenticate_user(
                [UserType.Administrator, UserType.Cashier, UserType.ShopManager]
            )
        )
    ],
)
async def attach_card(customer_id: str, card_id: str):
    """
    attach an existing user an existing card.

    - Permissions: all
    - Path parameter: customer_id (str) card_id (str)
    - Returns: Updated customer as CustomerResponseDTO
    - Raises:
      - NotFoundError: when the card or customer does not exist
      - BadRequestError: when card_id isn't integer string
    - Status code: 201 Created
    """
    updated = await controller.attach_card(customer_id, card_id)
    
    return updated


@router.patch(
    "/cards/{card_id}",
    status_code=status.HTTP_201_CREATED,
    dependencies=[
        Depends(
            authenticate_user(
                [UserType.Administrator, UserType.Cashier, UserType.ShopManager]
            )
        )
    ],
)
async def modify_point(card_id: str, points: int):
    """
    update point an existing card.

    - Permissions: all
    - Request body: CustomerCreateDTO (contains cardId, points)
    - Returns: Updated card as CustomerResponseDTO
    - Raises:
      - NotFoundError: when the card does not exist
      - BadRequestError: when card_id isn't integer string
    - Status code: 201 Created
    """

    updated = await controller.modify_point(card_id, points)
    
    return updated
