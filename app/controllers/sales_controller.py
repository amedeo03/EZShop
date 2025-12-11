from typing import List, Optional

from app.controllers.products_controller import ProductsController
from app.controllers.sold_products_controller import SoldProductsController
from app.models.DAO.sale_dao import SaleDAO
from app.models.DTO.boolean_response_dto import BooleanResponseDTO
from app.models.DTO.product_dto import ProductTypeDTO
from app.models.DTO.sale_dto import SaleDTO
from app.models.DTO.sold_product_dto import SoldProductDTO
from app.models.errors.bad_request import BadRequestError
from app.models.errors.insufficient_stock_error import InsufficientStockError
from app.models.errors.invalid_sale_status_error import InvalidSaleStatusError
from app.models.errors.notfound_error import NotFoundError
from app.repositories.sales_repository import SalesRepository
from app.services.input_validator_service import (
    validate_field_is_positive,
    validate_field_is_present,
    validate_product_barcode,
)
from app.services.mapper_service import sale_dao_to_dto


class SalesController:
    def __init__(self):
        self.repo = SalesRepository()
        self.sold_product_controller = SoldProductsController()
        self.product_controller = ProductsController()

    async def create_sale(self) -> SaleDTO:
        """
        Create a sale.

        - Parameters: none
        - Returns: SaleDTO
        """
        created_sale: SaleDAO = await self.repo.create_sale()
        return sale_dao_to_dto(created_sale)

    async def list_sales(self) -> List[SaleDTO]:
        """
        Returns a list of sales present in the database

        - Parameters: none
        - Returns: List[SaleDTO]
        """
        sales_dao: Optional[List[SaleDAO]] = await self.repo.list_sales()
        sales_dto: List[SaleDTO] = list()

        if not sales_dao:
            raise NotFoundError("Product not found")

        for sale_dao in sales_dao:
            sales_dto.append(sale_dao_to_dto(sale_dao))

        return sales_dto

    async def get_sale_by_id(self, sale_id: int) -> SaleDTO:
        """
        Returns a sale given its ID, or NotFound if not present

        - Parameters: sale_id as int
        - Returns: SaleDTO
        """
        validate_field_is_positive(sale_id, "product_id")
        sale: SaleDAO = await self.repo.get_sale_by_id(sale_id)
        return sale_dao_to_dto(sale)

    async def attach_product(
        self, sale_id: int, barcode: str, amount: int
    ) -> BooleanResponseDTO:
        """
        Attach a product to a given sale

        - Parameters: sale_id as int, barcode as str, amount as int
        - Returns: BooleanResponseDTO
        """
        validate_field_is_positive(sale_id, "product_id")
        validate_field_is_present(barcode, "barcode")
        validate_product_barcode(barcode)
        validate_field_is_positive(amount, "amount")

        sale: SaleDTO = await self.get_sale_by_id(sale_id)
        if sale.status != "OPEN":
            raise InvalidSaleStatusError("Selected sale status is not 'OPEN'")

        product: ProductTypeDTO = await self.product_controller.get_product_by_barcode(
            barcode
        )

        if product.quantity - amount < 0:
            raise InsufficientStockError(
                "Amount selected is greater than available stock"
            )

        if product.id == None:
            raise BadRequestError("Invalid product")

        sold_product: SoldProductDTO = (
            await self.sold_product_controller.create_sold_product(
                product.id, sale_id, product.barcode, amount, product.price_per_unit
            )
        )

        return (
            BooleanResponseDTO(success=True)
            if sold_product
            else BooleanResponseDTO(success=False)
        )

    async def delete_sale(self, sale_id: int) -> BooleanResponseDTO:

        sale: SaleDTO = await self.get_sale_by_id(sale_id)
        if sale.status == "PAID":
            raise BadRequestError("Selected sale status is 'PAID'")

        for product in sale.lines:
            # TODO:Waiting for /products/{id}/quantity implementation
            # self.product_controller.update_product_quantity(product.quantity, product.id)
            success: BooleanResponseDTO = (
                await self.sold_product_controller.delete_sold_product(
                    product.id, sale.id
                )
            )
            if success.success != True:
                return BooleanResponseDTO(success=False)

        return BooleanResponseDTO(success=True)
