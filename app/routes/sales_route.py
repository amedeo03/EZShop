from typing import List

from fastapi import APIRouter, Depends, HTTPException, Response, status

from app.config.config import ROUTES
from app.middleware.auth_middleware import authenticate_user
from app.models.errors.bad_request import BadRequestError
from app.models.errors.notfound_error import NotFoundError
from app.models.user_type import UserType

from app.models.DTO.sale_dto import SaleDTO
from app.models.DTO.sold_product_dto import SoldProductDTO
from app.controllers.sales_controller import SalesController


router = APIRouter(prefix=ROUTES['V1_SALES'], tags=["Sales"])
controller = SalesController()

@router.post("/", 
    response_model= SaleDTO,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(authenticate_user([UserType.Administrator, UserType.ShopManager, UserType.Cashier]))])
async def create_sale(sale: SaleDTO):
    """
    Starts a new sale transaction with initial status OPEN. Requires authentication as Administrator, ShopManager, or Cashier.
    Will return:
    - 201 saleDTO if creation is succesful;
    - 401 if unauthenticated.
    """
    
    return