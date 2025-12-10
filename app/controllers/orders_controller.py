from typing import List
from datetime import datetime

from app.models.DAO.order_dao import OrderDAO
from app.models.DTO.boolean_response_dto import BooleanResponseDTO
from app.models.DTO.order_dto import OrderDTO
from app.repositories.orders_repository import OrdersRepository
from app.models.errors.notfound_error import NotFoundError
from app.models.errors.app_error import AppError
from app.services.input_validator_service import (
    validate_field_is_positive,
    validate_product_barcode,
)

class OrdersController:
    def __init__(self):
        self.repo = OrdersRepository()

    async def create_order(self, order_dto: OrderDTO) -> OrderDTO:
        validate_product_barcode(order_dto.product_barcode)
        validate_field_is_positive(order_dto.quantity, "quantity")
        validate_field_is_positive(order_dto.price_per_unit, "price_per_unit")

        created_order_dao = await self.repo.create_order(
            product_barcode=order_dto.product_barcode,
            quantity=order_dto.quantity,
            price_per_unit=order_dto.price_per_unit,
            status=order_dto.status
        )

        return OrderDTO(
            id=created_order_dao.id,
            product_barcode=created_order_dao.product_barcode,
            quantity=created_order_dao.quantity,
            price_per_unit=created_order_dao.price_per_unit,
            status=created_order_dao.status,
            issue_date=created_order_dao.issue_date
        )

    async def list_orders(self) -> List[OrderDTO]:
        orders_daos = await self.repo.list_orders()
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
    
    async def pay_order(self, order_id: int) -> BooleanResponseDTO:
        validate_field_is_positive(order_id, "order_id")
        result = await self.repo.pay_order(order_id)
        return BooleanResponseDTO(success=result)

    async def record_arrival(self, order_id: int) -> BooleanResponseDTO:
        """
        Record the arrival of an order.
        """
        validate_field_is_positive(order_id, "order_id")

        # Validate state: Must be PAID
        order = await self.repo.get_order(order_id)
        if not order:
             raise NotFoundError(f"Order with id {order_id} not found")

        if order.status != "PAID":
            # Swagger 420: Invalid order state
            raise AppError("Order is not paid", 420)
            
        result = await self.repo.record_arrival(order_id)
        return BooleanResponseDTO(success=result)

    async def pay_order_for(self, order_dto: OrderDTO) -> OrderDTO:
        """
        Create and immediately pay for an order.
        """
        validate_product_barcode(order_dto.product_barcode)
        validate_field_is_positive(order_dto.quantity, "quantity")
        validate_field_is_positive(order_dto.price_per_unit, "price_per_unit")
        
        # Prepare DAO
        order_dao = OrderDAO(
            product_barcode=order_dto.product_barcode,
            quantity=order_dto.quantity,
            price_per_unit=order_dto.price_per_unit,
            status="PAID", # Initial state for this endpoint
            issue_date=datetime.now()
        )
        
        created_order_dao = await self.repo.create_and_pay_order(order_dao)

        return OrderDTO(
            id=created_order_dao.id,
            product_barcode=created_order_dao.product_barcode,
            quantity=created_order_dao.quantity,
            price_per_unit=created_order_dao.price_per_unit,
            status=created_order_dao.status,
            issue_date=created_order_dao.issue_date
        )