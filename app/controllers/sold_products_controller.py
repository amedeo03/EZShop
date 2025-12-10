from app.models.DTO.sold_product_dto import SoldProductDTO
from app.models.errors.notfound_error import NotFoundError
from app.repositories.sold_products_repository import SoldProductsRepository
from app.services.input_validator_service import (
    validate_field_is_positive,
    validate_field_is_present,
    validate_product_barcode,
    validate_product_position,
)
from app.services.mapper_service import sold_product_dao_to_dto


class SoldProductsController:
    def __init__(self):
        self.repo = SoldProductsRepository()

    async def create_sold_product(
        self, sold_product_dto: SoldProductDTO
    ) -> SoldProductDTO:
        """
        Create new sold product.

        - Parameters: sold_product_dto: SoldProductDTO
        - Returns: sold_product_dto: SoldProductDTO
        """

        validate_field_is_positive(sold_product_dto.id, "id")
        validate_field_is_positive(sold_product_dto.sale_id, "sale_id")
        validate_field_is_positive(sold_product_dto.quantity, "quantity")
        validate_product_barcode(sold_product_dto.product_barcode)
        validate_field_is_present(
            str(sold_product_dto.price_per_unit), "price_per_unit"
        )
        validate_field_is_positive(sold_product_dto.price_per_unit, "price_per_unit")
        validate_field_is_present(str(sold_product_dto.discount_rate), "discount_rate")
        validate_field_is_positive(sold_product_dto.discount_rate, "discount_rate")

        created_product = await self.repo.create_sold_product(
            sold_product_dto.id,
            sold_product_dto.sale_id,
            sold_product_dto.product_barcode,
            sold_product_dto.quantity,
            sold_product_dto.price_per_unit,
            sold_product_dto.discount_rate,
        )

        return sold_product_dao_to_dto(created_product)

    async def get_sold_product_by_id(self, product_id: int) -> SoldProductDTO:
        """
        Get sold product by id.
        - Parameters: product_id (int)
        - Returns: first sold product found as SoldProductDTO
        - Throws:
            - NotFoundError if product_id not found
            - BadRequestError if product_id is negative
        """
        validate_field_is_positive(product_id, "product_id")

        sold_product_dao = await self.repo.get_sold_product_by_id(product_id)

        if not sold_product_dao:
            raise NotFoundError("Product not found")

        return sold_product_dao_to_dto(sold_product_dao[0])

    async def get_sold_product_by_barcode(self, product_barcode: str) -> SoldProductDTO:
        """
        Get sold product by barcode.
        - Parameters: product_barcode (str)
        - Returns: first sold product found as SoldProductDTO
        - Throws:
            - NotFoundError if product_barcode not found
            - BadRequestError if barcode is not valid
        """
        validate_field_is_present(product_barcode, "product_barcode")
        validate_product_barcode(product_barcode)

        sold_product_dao = await self.repo.get_sold_product_by_barcode(product_barcode)

        if not sold_product_dao:
            raise NotFoundError("Product not found")

        return sold_product_dao_to_dto(sold_product_dao[0])
