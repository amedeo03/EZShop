from math import floor
from typing import List, Optional

from app.controllers.sold_products_controller import SoldProductsController
from app.models.DAO.sale_dao import SaleDAO
from app.models.DTO.boolean_response_dto import BooleanResponseDTO
from app.models.DTO.change_response_dto import ChangeResponseDTO
from app.models.DTO.points_response_dto import PointsResponseDTO
from app.models.DTO.product_dto import ProductTypeDTO
from app.models.DTO.sale_dto import SaleDTO
from app.models.DTO.sold_product_dto import SoldProductDTO
from app.models.errors.bad_request import BadRequestError
from app.models.errors.insufficient_stock_error import InsufficientStockError
from app.models.errors.invalid_state_error import InvalidStateError
from app.models.errors.notfound_error import NotFoundError
from app.repositories.sales_repository import SalesRepository
from app.services.input_validator_service import (
    validate_discount_rate,
    validate_field_is_positive,
    validate_field_is_present,
    validate_product_barcode,
)
from app.services.mapper_service import sale_dao_to_dto


class SalesController:
    def __init__(self):
        self.repo = SalesRepository()

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
            return []

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
        self,
        sale_id: int,
        barcode: str,
        amount: int,
        products_controller,
        sold_products_controller,
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

        inventory_product: ProductTypeDTO = None  # type: ignore
        sold_product: SoldProductDTO = None  # type: ignore
        sale: SaleDTO = await self.get_sale_by_id(sale_id)

        # sale checks
        if sale.status != "OPEN":
            raise InvalidStateError("Selected sale status is not 'OPEN'")

        inventory_product = await products_controller.get_product_by_barcode(barcode)

        # inventory checks
        if inventory_product.quantity - amount < 0:
            raise InsufficientStockError(
                "Amount selected is greater than available stock"
            )

        for product in sale.lines:
            if product.product_barcode == barcode:
                sold_product = product
                break
        
        if sold_product is not None:
            await sold_products_controller.edit_sold_product_quantity(
                sold_product.id, sold_product.sale_id, amount
            )
        else:
            await sold_products_controller.create_sold_product(
                inventory_product.id,
                sale_id,
                inventory_product.barcode,
                amount,
                inventory_product.price_per_unit,
            )

        await products_controller.update_product_quantity(inventory_product.id, -amount)
        return BooleanResponseDTO(success=True)

    async def delete_sale(
        self, sale_id: int, sold_products_controller, products_controller
    ) -> None:
        sale: SaleDTO = await self.get_sale_by_id(sale_id)
        if sale.status == "PAID":
            raise InvalidStateError("Selected sale status is not 'PAID'")

        for sold_product in sale.lines:
            # remove sold product
            await sold_products_controller.remove_sold_product(sale.id, sold_product.id)
            # restore inventory quantity
            await products_controller.update_product_quantity(sold_product.id,
                sold_product.quantity
            )

        await self.repo.delete_sale(sale_id)

    async def remove_sold_product_quantity(
        self,
        sale_id: int,
        barcode: str,
        amount: int,
        sold_products_controller,
        products_controller,
    ) -> BooleanResponseDTO:
        validate_field_is_positive(amount, "amount")

        await self.edit_sold_product_quantity(
            sale_id, barcode, -amount, sold_products_controller, products_controller
        )
        return BooleanResponseDTO(success=True)

    async def edit_sold_product_quantity(
        self,
        sale_id: int,
        barcode: str,
        amount: int,
        sold_products_controller,
        products_controller,
    ) -> BooleanResponseDTO:
        validate_field_is_positive(sale_id, "product_id")
        validate_field_is_present(barcode, "barcode")
        validate_product_barcode(barcode)

        product_to_edit: Optional[SoldProductDTO] = None

        sale: SaleDTO = await self.get_sale_by_id(sale_id)
        if sale.status != "OPEN":
            raise InvalidStateError("Selected sale status is not 'OPEN'")

        for product in sale.lines:
            if product.product_barcode == barcode:
                product_to_edit = product
                product_in_inventory = await products_controller.get_product_by_barcode(
                    product.product_barcode
                )
                break

        if product_to_edit is None:
            raise NotFoundError(
                "product barcode '{barcode}' not found in sale {sale_id}"
            )

        if product_to_edit.quantity + amount < 0:
            raise InsufficientStockError("insufficient quantity present in sale")
        if product_in_inventory.quantity - amount < 0:
            raise InsufficientStockError("insufficient stock in inventory")

        await sold_products_controller.edit_sold_product_quantity(
            product_to_edit.id, sale.id, amount
        )
        await products_controller.update_product_quantity(product_to_edit.id, -amount)

        return BooleanResponseDTO(success=True)

    async def edit_sale_discount(
        self, sale_id: int, discount_rate: float
    ) -> BooleanResponseDTO:
        validate_field_is_present(str(sale_id), "sale_id")
        validate_field_is_positive(sale_id, "sale_id")
        validate_discount_rate(discount_rate)

        await self.repo.edit_sale_discount(sale_id, discount_rate)

        return BooleanResponseDTO(success=True)

    async def edit_product_discount(
        self,
        sale_id: int,
        product_barcode: str,
        discount_rate: float,
        sold_products_controller,
    ) -> BooleanResponseDTO:
        validate_field_is_present(str(sale_id), "sale_id")
        validate_field_is_positive(sale_id, "sale_id")
        validate_field_is_present(product_barcode, "product_barcode")
        validate_product_barcode(product_barcode)
        validate_discount_rate(discount_rate)

        product_to_edit: SoldProductDTO = None  # type: ignore
        sale: SaleDTO = await self.get_sale_by_id(sale_id)
        if sale.status != "OPEN":
            raise InvalidStateError("Selected sale status is not 'OPEN'")

        for product in sale.lines:
            if product.product_barcode == product_barcode:
                product_to_edit = product
                break

        if product_to_edit == None:
            raise NotFoundError("")
        success: BooleanResponseDTO = (
            await sold_products_controller.edit_sold_product_discount(
                product_to_edit.id, sale.id, discount_rate
            )
        )

        return BooleanResponseDTO(success=True)

    async def close_sale(
        self, sale_id: int, products_controller, sold_products_controller
    ) -> BooleanResponseDTO:
        validate_field_is_present(str(sale_id), "sale_id")
        validate_field_is_positive(sale_id, "sale_id")

        sale: SaleDTO = await self.get_sale_by_id(sale_id)
        if sale.status != "OPEN":
            raise InvalidStateError("Selected sale status is not 'OPEN'")

        if len(sale.lines) == 0:
            await self.delete_sale(
                sale_id, sold_products_controller, products_controller
            )
        else:
            await self.repo.edit_sale_status(sale_id, "PENDING")

        return BooleanResponseDTO(success=True)

    async def pay_sale(self, sale_id: int, cash_amount: float) -> ChangeResponseDTO:
        validate_field_is_present(str(sale_id), "sale_id")
        validate_field_is_positive(sale_id, "sale_id")
        validate_field_is_positive(cash_amount, "cash_amount")

        sale: SaleDTO = await self.get_sale_by_id(sale_id)
        if sale.status != "PENDING":
            raise InvalidStateError("Selected sale status is not 'PENDING'")

        amount_needed: float = await self.get_sale_value(sale_id)
        change: float = cash_amount - amount_needed
        if change >= 0:
            await self.repo.edit_sale_status(sale_id, "PAID")
        else:
            raise BadRequestError("amount is not enough to pay the sale")

        return ChangeResponseDTO(change=round(change, 2))

    async def get_sale_value(self, sale_id: int) -> float:
        validate_field_is_present(str(sale_id), "sale_id")
        validate_field_is_positive(sale_id, "sale_id")

        value: float = 0.0
        sale: SaleDTO = await self.get_sale_by_id(sale_id)

        if len(sale.lines) == 0:
            return 0.0

        for product in sale.lines:
            value += (
                product.quantity * product.price_per_unit * (1 - product.discount_rate)
            )

        value = value * (1 - sale.discount_rate)
        return value

    async def get_points(self, sale_id: int) -> PointsResponseDTO:
        validate_field_is_present(str(sale_id), "sale_id")
        validate_field_is_positive(sale_id, "sale_id")

        points: int = 0
        sale: SaleDTO = await self.get_sale_by_id(sale_id)

        if sale.status != "PAID":
            raise InvalidStateError("Selected sale is not 'PAID'")
        points = floor(await self.get_sale_value(sale_id) / 10)

        return PointsResponseDTO(points=points)
