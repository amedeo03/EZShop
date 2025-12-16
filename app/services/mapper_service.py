from typing import List

from sqlalchemy import Column

from app.models.DAO.card_dao import CardDAO
from app.models.DAO.customer_dao import CustomerDAO
from app.models.DAO.product_dao import ProductDAO
from app.models.DAO.sale_dao import SaleDAO
from app.models.DAO.sold_product_dao import SoldProductDAO
from app.models.DAO.user_dao import UserDAO
from app.models.DAO.return_transaction_dao import ReturnTransactionDAO
from app.models.DTO.return_transaction_dto import ReturnTransactionDTO
from app.models.DTO.returned_product_dto import ReturnedProductDTO
from app.models.DAO.returned_product_dao import ReturnedProductDAO
from app.models.DTO.card_dto import CardDTO
from app.models.DTO.customer_dto import CustomerDTO
from app.models.DTO.error_dto import ErrorDTO
from app.models.DTO.product_dto import ProductTypeDTO
from app.models.DTO.sale_dto import SaleDTO
from app.models.DTO.sold_product_dto import SoldProductDTO
from app.models.DTO.token_dto import TokenDTO
from app.models.DTO.user_dto import UserDTO



def create_error_dto(code: int, message: str, name: str) -> ErrorDTO:
    """Create an ErrorDTO instance"""
    return ErrorDTO(code=code, message=message, name=name)


def create_token_dto(token: str) -> TokenDTO:
    return TokenDTO(token=token)


def userdao_to_dto(user_dao: UserDAO) -> UserDTO:
    return UserDTO(
        id=user_dao.id,
        username=user_dao.username,
        password=user_dao.password,
        type=user_dao.type,
    )


def userdao_to_responsedto(user_dao: UserDAO) -> UserDTO:
    return UserDTO(id=user_dao.id, username=user_dao.username, type=user_dao.type)


def customerdao_to_responsedto(
    customer_dao: CustomerDAO, card_dao: CardDAO
) -> CustomerDTO:
    return CustomerDTO(
        id=customer_dao.id,
        name=customer_dao.name,
        card=carddao_to_responsedto(card_dao) if card_dao else None,
    )


def carddao_to_responsedto(card_dao: CardDAO) -> CardDTO:
    return CardDTO(cardId=card_dao.cardId, points=card_dao.points)


def productdao_to_product_type_dto(product_dao: ProductDAO) -> ProductTypeDTO:
    return ProductTypeDTO(
        id=product_dao.id,
        description=product_dao.description,
        barcode=product_dao.barcode,
        price_per_unit=product_dao.price_per_unit,
        note=product_dao.note,
        quantity=product_dao.quantity,
        position=product_dao.position,
    )


def sale_dao_to_dto(sale_dao: SaleDAO) -> SaleDTO:
    return SaleDTO.model_validate(sale_dao)


def sold_product_dao_to_dto(sold_product_dao: SoldProductDAO) -> SoldProductDTO:
    return SoldProductDTO.model_validate(sold_product_dao)

def return_transaction_dao_to_return_transaction_dto(return_transaction_dao: ReturnTransactionDAO) -> ReturnTransactionDTO:
    return ReturnTransactionDTO.model_validate(return_transaction_dao)

def returned_product_dao_to_dto(returned_product_dao: ReturnedProductDAO) -> ReturnedProductDTO:
    return ReturnedProductDTO.model_validate(returned_product_dao)

'''
    return ReturnTransactionDTO(
        id=return_transaction_dao.id,
        sale_id=return_transaction_dao.sale_id,
        status=return_transaction_dao.status,
        created_at=return_transaction_dao.created_at,
        closed_at=return_transaction_dao.closed_at,
        lines=return_transaction_dao.lines
    )
'''
