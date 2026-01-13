from app.models.DTO.boolean_response_dto import BooleanResponseDTO
from app.models.DTO.sold_product_dto import SoldProductDTO
from app.models.errors.notfound_error import NotFoundError
from app.repositories.sold_products_repository import SoldProductsRepository
from app.services.input_validator_service import (
    validate_discount_rate,
    validate_field_is_positive,
    validate_field_is_present,
    validate_product_barcode,
)
from app.services.mapper_service import sold_product_dao_to_dto


class SoldProductsController:
    def __init__(self):
        self.repo = SoldProductsRepository()

    async def create_sold_product(
        self,
        id: int,
        sale_id: int,
        product_barcode: str,
        quantity: int,
        price_per_unit: float,
    ) -> SoldProductDTO:
        """
        Create new sold product.

        - Parameters: sold_product_dto: SoldProductDTO
        - Returns: sold_product_dto: SoldProductDTO
        """

        validate_field_is_positive(id, "id")
        validate_field_is_positive(sale_id, "sale_id")
        validate_field_is_positive(quantity, "quantity")
        validate_field_is_present(product_barcode, "product_barcode")
        validate_product_barcode(product_barcode)
        validate_field_is_present(str(price_per_unit), "price_per_unit")
        validate_field_is_positive(price_per_unit, "price_per_unit")

        product = await self.repo.create_sold_product(
            id,
            sale_id,
            product_barcode,
            quantity,
            price_per_unit,
            0.0,
        )

        return sold_product_dao_to_dto(product)

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

    async def get_sold_product(self, product_id: int, sale_id: int) -> SoldProductDTO:
        """
        Get sold product by id and sale_id.
        - Parameters: product_id (int)
        - Returns: sold product found as SoldProductDTO
        - Throws:
            - NotFoundError if product_id not found
            - BadRequestError if product_id is negative
        """
        validate_field_is_positive(product_id, "product_id")
        validate_field_is_positive(sale_id, "sale_id")

        sold_product_dao = await self.repo.get_sold_product(product_id, sale_id)

        if not sold_product_dao:
            raise NotFoundError("Product not found")

        return sold_product_dao_to_dto(sold_product_dao)

    async def get_sold_product_by_sale_barcode(
        self, sale_id: int, barcode: str
    ) -> SoldProductDTO:
        """
        Get sold product sale_id and barcode.
        - Returns: sold product found as SoldProductDTO
        - Throws:
            - NotFoundError if product_id not found
            - BadRequestError if product_id is negative
        """
        validate_field_is_present(barcode, "product_barcode")
        validate_product_barcode(barcode)
        validate_field_is_positive(sale_id, "sale_id")

        sold_product_dao = await self.repo.get_sold_product_by_sale_barcode(
            sale_id, barcode
        )

        if not sold_product_dao:
            raise NotFoundError("Product not found")

        return sold_product_dao_to_dto(sold_product_dao)

    async def edit_sold_product_quantity(
        self, id: int, sale_id: int, quantity: int
    ) -> BooleanResponseDTO:
        validate_field_is_present(str(id), "product_id")
        validate_field_is_positive(id, "product_id")
        validate_field_is_present(str(sale_id), "sale_id")
        validate_field_is_positive(sale_id, "sale_id")
        validate_field_is_present(str(quantity), "sale_id")

        success: BooleanResponseDTO = await self.repo.edit_sold_product_quantity(
            id, sale_id, quantity
        )

        return (
            BooleanResponseDTO(success=True)
            if BooleanResponseDTO(success=True)
            else BooleanResponseDTO(success=False)
        )

    async def edit_sold_product_discount(
        self, id: int, sale_id: int, discount_rate: float
    ) -> BooleanResponseDTO:
        validate_field_is_present(str(id), "product_id")
        validate_field_is_positive(id, "product_id")
        validate_field_is_present(str(sale_id), "sale_id")
        validate_discount_rate(discount_rate)

        success: BooleanResponseDTO = await self.repo.edit_sold_product_discount(
            id, sale_id, discount_rate
        )

        return (
            BooleanResponseDTO(success=True)
            if BooleanResponseDTO(success=True)
            else BooleanResponseDTO(success=False)
        )

    async def remove_sold_product(self, sale_id: int, id: int) -> None:
        validate_field_is_present(str(id), "product_id")
        validate_field_is_positive(id, "product_id")
        validate_field_is_present(str(sale_id), "sale_id")
        validate_field_is_positive(sale_id, "sale_id")

        await self.repo.remove_sold_product(sale_id, id)
        return
