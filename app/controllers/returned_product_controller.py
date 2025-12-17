from app.models.DTO.boolean_response_dto import BooleanResponseDTO
from app.models.errors.notfound_error import NotFoundError
from app.repositories.returned_products_repository import ReturnedProductsRepository
from app.models.DTO.returned_product_dto import ReturnedProductDTO
from app.services.input_validator_service import (
    validate_discount_rate,
    validate_field_is_positive,
    validate_field_is_present,
    validate_product_barcode,
)
from app.services.mapper_service import returned_product_dao_to_dto
from typing import List


class ReturnedProductController:
    def __init__(self):
        self.repo = ReturnedProductsRepository()
    async def create_returned_product(
        self,
        id: int,
        return_id: int,
        product_barcode: str,
        quantity: int,
        price_per_unit: float,
    ) -> ReturnedProductDTO:
        """
        Create new returned product.

        - Parameters: returned_product_dto: ReturnedProductDTO
        - Returns: returned_product_dto: ReturnedProductDTO
        """

        validate_field_is_positive(id, "id")
        validate_field_is_positive(return_id, "return_id")
        validate_field_is_positive(quantity, "quantity")
        validate_product_barcode(product_barcode)
        validate_field_is_present(str(price_per_unit), "price_per_unit")
        validate_field_is_positive(price_per_unit, "price_per_unit")

        created_product = await self.repo.create_returned_product(
            id,
            return_id,
            product_barcode,
            quantity,
            price_per_unit,
        )

        return returned_product_dao_to_dto(created_product)

    async def get_returned_products_by_id(self, product_id: int) -> List[ReturnedProductDTO]:
        """
        Get returned product by id.
        - Parameters: product_id (int)
        - Returns: list of returned products found as ReturnedProductDTO
        - Throws:
            - NotFoundError if product_id not found
            - BadRequestError if product_id is negative
        """
        validate_field_is_positive(product_id, "product_id")

        returned_product_dao = await self.repo.get_returned_products_by_id(product_id)

        if not returned_product_dao:
            raise NotFoundError("Product not found")

        return [returned_product_dao_to_dto(rpd) for rpd in returned_product_dao]

    async def get_returned_product_by_barcode(self, product_barcode: str) -> List[ReturnedProductDTO]:
        """
        Get returned product by barcode.
        - Parameters: product_barcode (str)
        - Returns: list of returned products found as ReturnedProductDTO
        - Throws:
            - NotFoundError if product_barcode not found
            - BadRequestError if barcode is not valid
        """
        validate_field_is_present(product_barcode, "product_barcode")
        validate_product_barcode(product_barcode)

        returned_product_dao = await self.repo.get_returned_product_by_barcode(product_barcode)

        if not returned_product_dao:
            raise NotFoundError("Product not found")

        return [returned_product_dao_to_dto(rpd) for rpd in returned_product_dao]