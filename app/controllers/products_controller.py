from typing import List

from app.models.DTO.boolean_response_dto import BooleanResponseDTO
from app.models.DTO.product_dto import (
    ProductCreateDTO,
    ProductTypeDTO,
    ProductUpdateDTO,
)
from app.models.errors.invalid_state_error import InvalidStateError
from app.models.errors.notfound_error import NotFoundError
from app.repositories.products_repository import ProductsRepository
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

    async def create_product(self, product_dto: ProductCreateDTO) -> ProductTypeDTO:
        """
        Create a product.

        - Parameters: product_dto (ProductCreateDTO)
        - Returns: The created product as ProductCreateDTO
        - Throws:
            - BadRequestError if description/price_per_unit is not present, if barcode is invalid (GTIN) or not a string of 12-14 digits
        """

        validate_field_is_present(product_dto.description, "description")
        validate_field_is_present(product_dto.price_per_unit, "price_per_unit")
        validate_field_is_positive(product_dto.price_per_unit, "price_per_unit")
        validate_field_is_present(product_dto.barcode, "barcode")
        validate_product_barcode(product_dto.barcode)

        if product_dto.position is not None:
            validate_product_position(product_dto.position)

        if product_dto.quantity is not None and product_dto.quantity != 0:
            validate_field_is_positive(product_dto.quantity, "quantity")

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

        validate_field_is_positive(product_id, "product_id")

        product_dao = await self.repo.get_product(product_id)
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

    async def update_product_position(
        self, product_id: int, position: str
    ) -> BooleanResponseDTO:
        """
        Update the position of a product.
        - Parameters: product_id (int), position (str)
        - Returns: Result of the operation as BooleanResponseDTO
        - Throws:
            - BadRequestError if product_id is negative, not a string or position pattern is wrong
        """

        validate_field_is_positive(product_id, "product_id")
        validate_product_position(position)

        updated_product = await self.repo.update_product_position(product_id, position)

        if updated_product:
            return BooleanResponseDTO(success=True)

    async def update_product_quantity(
        self, product_id: int, quantity: int
    ) -> BooleanResponseDTO:
        """
        Update the quantity of a product.
        - Parameters: product_id (int), quantity (int)
        - Returns: Result of the operation as BooleanResponseDTO
        - Throws:
            - BadRequestError if product_id/quantity are negative or not they are not integers
        """
        validate_field_is_positive(product_id, "product_id")

        updated_product = await self.repo.update_product_quantity(product_id, quantity)

        if updated_product:
            return BooleanResponseDTO(success=True)

    async def update_product(
        self,
        product_id: int,
        product_dto: ProductUpdateDTO,
        sold_products_controller,
        orders_controller,
        returned_products_controller,
    ) -> BooleanResponseDTO:
        """
        Update existing product.
        - Returns: BooleanResponseDTO
        - Throws:
            - BadRequestError: if product_id < 0 or fields are invalid (description, price_per_unit, barcode).
            - InvalidStateError: if there are sales, orders, returns associated with the product to update.
        """

        validate_field_is_positive(product_id, "product_id")
        validate_field_is_present(product_dto.barcode, "barcode")
        validate_product_barcode(product_dto.barcode)

        if product_dto.price_per_unit is not None:
            validate_field_is_positive(product_dto.price_per_unit, "price_per_unit")

        if product_dto.quantity is not None:
            validate_field_is_positive(product_dto.quantity, "quantity")

        if product_dto.position is not None:
            validate_product_position(product_dto.position)

        try:
            # The product has NO sales associated with it.
            result = await sold_products_controller.get_sold_product_by_id(product_id)

            if result:
                raise InvalidStateError(
                    f"There is an existing SALE for 'product_id' '{product_id}'"
                )
        except NotFoundError:
            pass

        try:
            # The product has NO orders associated with it.
            product_db = await self.get_product(product_id)
            product_barcode_on_db = product_db.barcode

            existing_order = await orders_controller.get_order_by_product_barcode(
                product_barcode_on_db
            )
            if existing_order:
                raise InvalidStateError(
                    f"There is an existing ORDER for 'product_id' '{product_id}'"
                )
        except NotFoundError:
            pass

        try:
            # The product has NO returns associated with it.
            existing_return = (
                await returned_products_controller.get_returned_products_by_id(
                    product_id
                )
            )

            if existing_return:
                raise InvalidStateError(
                    f"There is an existing RETURN for 'product_id' '{product_id}'"
                )

        except NotFoundError:
            # no sales, orders, returns found, updating the product
            await self.repo.update_product(
                product_id=product_id, product_update_dto=product_dto
            )

        return BooleanResponseDTO(success=True)

    async def delete_product(
        self,
        product_id: int,
        sold_products_controller,
        orders_controller,
        returned_products_controller,
    ) -> None:
        """
        Delete existing product.
        - Throws:
            - BadRequestError: if product_id < 0.
            - InvalidStateError: if there are sales, orders, returns associated with the product to delete.
        """

        validate_field_is_positive(product_id, "product_id")

        try:
            # The product has NO sales associated with it.
            result = await sold_products_controller.get_sold_product_by_id(product_id)

            if result:
                raise InvalidStateError(
                    f"There is an existing SALE for 'product_id' '{product_id}'"
                )
        except NotFoundError:
            pass

        try:
            # The product has NO orders associated with it.
            product_db = await self.get_product(product_id)
            product_barcode_on_db = product_db.barcode

            existing_order = await orders_controller.get_order_by_product_barcode(
                product_barcode_on_db
            )
            if existing_order:
                raise InvalidStateError(
                    f"There is an existing ORDER for 'product_id' '{product_id}'"
                )
        except NotFoundError:
            pass

        try:
            # The product has NO returns associated with it.
            existing_return = (
                await returned_products_controller.get_returned_products_by_id(
                    product_id
                )
            )

            if existing_return:
                raise InvalidStateError(
                    f"There is an existing RETURN for 'product_id' '{product_id}'"
                )

        except NotFoundError:  # no sales, orders, returns found, updating the product
            await self.repo.delete_product(product_id=product_id)
