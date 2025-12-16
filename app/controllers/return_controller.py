from typing import List

from app.models.DTO.boolean_response_dto import BooleanResponseDTO
from ezshop.app.models.DTO.return_transaction_dto import ReturnTransactionDTO
from app.models.errors.bad_request import BadRequestError
from app.models.errors.notfound_error import NotFoundError
# missing
from app.repositories.return_repository import ReturnRepository
from app.services.gtin_service import gtin
from app.services.input_validator_service import (
    validate_field_is_positive,
)
from app.services.mapper_service import return_transaction_dao_to_return_transaction_dto


class ReturnController:
    def __init__(self):
        self.repo = ReturnRepository()

    async def create_return_transaction(self, sale_id: int) -> ReturnTransactionDTO:
        """
        Create a new return transaction.

        - Parameters: return_transaction (ReturnDTO)
        - Returns: ReturnDTO
        """

        new_return_transaction = await self.repo.create_return_transaction(
            sale_id=sale_id
        )
        return return_transaction_dao_to_return_transaction_dto(new_return_transaction)