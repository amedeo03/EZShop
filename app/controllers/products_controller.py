from typing import List

from app.models.DTO.boolean_response_dto import BooleanResponseDTO
from app.models.DTO.product_dto import ProductTypeDTO
from app.models.errors.bad_request import BadRequestError
from app.models.errors.notfound_error import NotFoundError
from app.repositories.products_repository import ProductsRepository
from app.services.gtin_service import gtin
from app.services.input_validator_service import (
    validate_field_is_positive,
    validate_field_is_present,
    validate_product_barcode,
    validate_product_position,
)
from app.services.mapper_service import productdao_to_product_type_dto


class ProductsController:
    def __init__(self):
        self.repo = ProductsRepository()

    async def create_product(self, product_dto: ProductTypeDTO) -> ProductTypeDTO:
        """
        Create a product.

        - Parameters: product_dto (ProductTypeDTO)
        - Returns: The created product as ProductTypeDTO
        - Throws:
            - BadRequestError if description/price_per_unit is not present, if barcode is invalid (GTIN) or not a string of 12-14 digits
        """

        validate_field_is_present(product_dto.description, "description")
        validate_field_is_present(product_dto.price_per_unit, "price_per_unit")
        validate_product_barcode(product_dto.barcode)
        validate_product_position(product_dto.position)
        validate_field_is_positive(product_dto.price_per_unit, "price_per_unit")

        created_product = await self.repo.create_product(
            product_dto.description,
            product_dto.barcode,
            product_dto.price_per_unit,
            product_dto.note,
            product_dto.quantity,
            product_dto.position,
        )
        return productdao_to_product_type_dto(created_product)

    async def list_products(self) -> List[ProductTypeDTO]:
        """Get all products
        - Parameters: product_dto (ProductTypeDTO)
        - Returns: All products as List[ProductTypeDTO]
        """
        product_daos = await self.repo.list_products()
        return [productdao_to_product_type_dto(dao) for dao in product_daos]

    async def get_product(self, product_id: int) -> ProductTypeDTO:
        """Get product by id.
        - Parameters: product_id (int)
        - Returns Found product as ProductTypeDTO
        - Throws:
            - NotFoundError if product_id not found
            - BadRequestError if product_id is negative
        """
        try:
            product_id = int(product_id)
        except ValueError:
            raise BadRequestError("product_id must be an integer.")

        validate_field_is_positive(product_id, "product_id")

        product_dao = await self.repo.get_product(product_id)
        if not product_dao:
            raise NotFoundError("Product not found")
        return productdao_to_product_type_dto(product_dao)

    async def get_product_by_barcode(self, barcode: str) -> ProductTypeDTO:
        """Get product by barcode.
        - Parameters: barcode (str)
        - Returns: Found requested product as ProdocutTypeDTO
        """
        validate_product_barcode(barcode)

        product_dao = await self.repo.get_product_by_barcode(barcode)

        return productdao_to_product_type_dto(product_dao)

    async def get_product_by_description(
        self, description: str
    ) -> List[ProductTypeDTO]:
        """Get product by description.
        - Parameters: barcode (str)
        - Returns: List[ProdocutTypeDTO] of products found
        - Throws: NotFoundError if product with partial description not found
        """
        products_daos = await self.repo.get_product_by_description(description)

        if not products_daos:
            raise NotFoundError("Products not found")
        return [productdao_to_product_type_dto(dao) for dao in products_daos]

    async def update_product_position(self, product_id, position) -> BooleanResponseDTO:
        """
        Update the position of a product.
        - Parameters: product_id (int), position (str)
        - Returns: Result of the operation as BooleanResponseDTO
        - Throws:
            - BadRequestError if product_id is negative, not a string or position pattern is wrong
        """
        try:
            product_id = int(product_id)
        except ValueError:
            raise BadRequestError("product_id must be an integer.")
        validate_field_is_positive(product_id, "product_id")
        validate_product_position(position)

        updated_product = await self.repo.update_product_position(product_id, position)

        if updated_product:
            return BooleanResponseDTO(success=True)

    async def update_product(
        self, product_id: int, product_dto: ProductTypeDTO
    ) -> BooleanResponseDTO:
        """Update existing product.
        - Returns: BooleanResponseDTO
        - Raises:
            - BadRequestError: if product_id < 0 or fields are invalid (description, pricePerUnit, barcode).
            - NotFoundError: if product_id not found.
            - ConflictError: if new barcode already exists
        """
        if len(product_dto.productCode) < 12 or len(product_dto.productCode) > 14:
            raise BadRequestError("productCode must be a string of 12-14 digits")
        gtin_result = gtin(product_dto.productCode)
        if product_id < 0 or product_id is None:
            raise BadRequestError("product_id must be positive")
        if not gtin_result:
            raise BadRequestError("Wrong barcode format (GTIN)")
        if product_dto.description is None or product_dto.description == "":
            raise BadRequestError("description is a mandatory field")
        if product_dto.pricePerUnit is None or product_dto.pricePerUnit == "":
            raise BadRequestError("pricePerUnit type is a mandatory field")
        # TODO: barcode can be updated ONLY IF there aren't returns, oreders or sales associated with it!
        # TODO:

        updated = await self.repo.update_product(
            product_dto.description,
            product_dto.productCode,
            product_dto.pricePerUnit,
            product_dto.note,
            product_dto.quantity,
            product_dto.position,
            product_id,
        )
        return (
            BooleanResponseDTO(success=True)
            if updated
            else BooleanResponseDTO(success=False)
        )
