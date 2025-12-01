from app.models.DAO.user_dao import UserDAO
from app.models.DAO.product_dao import ProductDAO
from app.models.DTO.product_dto import ProductTypeDTO

from app.models.DTO.user_dto import UserDTO
from app.models.DTO.token_dto import TokenDTO
from app.models.DTO.error_dto import ErrorDTO


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
        type=user_dao.type
    )


def userdao_to_responsedto(user_dao: UserDAO) -> UserDTO:
    return UserDTO(
        id=user_dao.id,
        username=user_dao.username,
        type=user_dao.type
    )


def productdao_to_product_type_dto(product_dao: ProductDAO) -> ProductTypeDTO:
    return ProductTypeDTO(
        id=product_dao.id,
        description=product_dao.description,
        productCode=product_dao.productCode,
        pricePerUnit=float(product_dao.pricePerUnit),
        note=product_dao.note,
        quantity=product_dao.quantity,
        position=product_dao.position
    )
