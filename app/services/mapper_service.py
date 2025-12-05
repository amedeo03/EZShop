from app.models.DAO.user_dao import UserDAO
from app.models.DTO.user_dto import UserDTO
from app.models.DAO.customer_dao import CustomerDAO
from app.models.DTO.customer_dto import CustomerDTO
from app.models.DAO.card_dao import CardDAO
from app.models.DTO.card_dto import CardDTO
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

def customerdao_to_responsedto(customer_dao: CustomerDAO,card_dao: CardDAO) -> CustomerDTO:
    return CustomerDTO(
        id=customer_dao.id,
        name=customer_dao.name,
        card=carddao_to_responsedto(card_dao) if card_dao else None
    )
def carddao_to_responsedto(card_dao: CardDAO)-> CardDTO:
    return CardDTO(
        cardId=card_dao.cardId,
        points=card_dao.points
    )