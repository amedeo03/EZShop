from typing import List

from app.models.DTO.order_dto import OrderDTO
from app.repositories.orders_repository import OrdersRepository
from app.services.input_validator_service import (
    validate_field_is_positive,
    validate_product_barcode,
)

class OrdersController:
    def __init__(self):
        self.repo = OrdersRepository()

    async def create_order(self, order_dto: OrderDTO) -> OrderDTO:
        """
        Create an order.
        - Parameters: order_dto (OrderDTO)
        - Returns: OrderDTO
        """
        # Validate Input using your project's existing validator service
        validate_product_barcode(order_dto.product_barcode)
        validate_field_is_positive(order_dto.quantity, "quantity")
        validate_field_is_positive(order_dto.price_per_unit, "price_per_unit")

        # Call Repository to save data
        created_order_dao = await self.repo.create_order(
            product_barcode=order_dto.product_barcode,
            quantity=order_dto.quantity,
            price_per_unit=order_dto.price_per_unit,
            status=order_dto.status
        )

        # Convert DAO (Database Object) back to DTO (API Object)
        return OrderDTO(
            id=created_order_dao.id,
            product_barcode=created_order_dao.product_barcode,
            quantity=created_order_dao.quantity,
            price_per_unit=created_order_dao.price_per_unit,
            status=created_order_dao.status,
            issue_date=created_order_dao.issue_date
        )

    async def list_orders(self) -> List[OrderDTO]:
        """
        Get all orders.
        - Returns: List[OrderDTO]
        """
        orders_daos = await self.repo.list_orders()
        
        # Convert list of DAOs to list of DTOs
        return [
            OrderDTO(
                id=dao.id,
                product_barcode=dao.product_barcode,
                quantity=dao.quantity,
                price_per_unit=dao.price_per_unit,
                status=dao.status,
                issue_date=dao.issue_date
            ) for dao in orders_daos
        ]