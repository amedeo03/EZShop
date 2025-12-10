from typing import Optional, List
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.database import AsyncSessionLocal
from app.models.DAO.order_dao import OrderDAO
from app.models.DAO.product_dao import ProductDAO
from app.models.DAO.system_dao import SystemInfoDAO
from app.models.errors.notfound_error import NotFoundError
from app.models.errors.balance_error import BalanceError
from app.models.errors.app_error import AppError

class OrdersRepository:

    def __init__(self, session: Optional[AsyncSession] = None):
        self._session = session

    async def _get_session(self) -> AsyncSession:
        return self._session or AsyncSessionLocal()

    async def create_order(
        self,
        product_barcode: str,
        quantity: int,
        price_per_unit: float,
        status: str
    ) -> OrderDAO:
        async with await self._get_session() as session:
            new_order = OrderDAO(
                product_barcode=product_barcode,
                quantity=quantity,
                price_per_unit=price_per_unit,
                status=status,
                issue_date=datetime.now()
            )
            session.add(new_order)
            await session.commit()
            await session.refresh(new_order)
            return new_order

    async def list_orders(self) -> List[OrderDAO]:
        async with await self._get_session() as session:
            result = await session.execute(select(OrderDAO))
            return result.scalars().all()
    
    async def get_order(self, order_id: int) -> Optional[OrderDAO]:
        """Helper to get order by ID"""
        async with await self._get_session() as session:
            return await session.get(OrderDAO, order_id)

    async def pay_order(self, order_id: int) -> bool:
        async with await self._get_session() as session:
            order = await session.get(OrderDAO, order_id)
            if not order:
                raise NotFoundError(f"Order with id {order_id} not found")

            if order.status != "ISSUED":
                # Matches signature in app_error.py: message, status_code
                raise AppError("Order was not Issued", 420)

            cost = order.quantity * order.price_per_unit

            result = await session.execute(select(SystemInfoDAO))
            system_info = result.scalars().first()
            
            if not system_info:
                raise BalanceError("System balance information not found")

            if system_info.balance < cost:
                raise BalanceError("Insufficient balance for the operation")

            system_info.balance -= cost
            order.status = "PAID"
            
            await session.commit()
            return True

    async def record_arrival(self, order_id: int) -> bool:
        """
        Record the arrival of an order:
        1. Validates order exists.
        2. Updates the product quantity (restock).
        3. Sets order status to COMPLETED.
        """
        async with await self._get_session() as session:
            order = await session.get(OrderDAO, order_id)
            if not order:
                return False 
            
            # Match Order's product_barcode with Product's barcode
            result = await session.execute(
                select(ProductDAO).where(ProductDAO.barcode == order.product_barcode)
            )
            product = result.scalars().first()
            
            if product:
                # Swagger 500 Error Requirement: Position must be set
                if not product.position:
                     raise AppError("Position must be set for an order before its arrival", 500)

                product.quantity += order.quantity

            order.status = "COMPLETED"
            
            await session.commit()
            return True

    async def create_and_pay_order(self, order_dao: OrderDAO) -> OrderDAO:
        """
        Atomic transaction: Check Balance -> Deduct Cost -> Create PAID Order
        """
        async with await self._get_session() as session:
            cost = order_dao.quantity * order_dao.price_per_unit
            
            result = await session.execute(select(SystemInfoDAO))
            system_info = result.scalars().first()
            
            # Lazy Init if missing
            if not system_info:
                 system_info = SystemInfoDAO(balance=0.0)
                 session.add(system_info)

            if system_info.balance < cost:
                raise BalanceError("Insufficient balance for the operation")

            system_info.balance -= cost
            
            # Force status to PAID
            order_dao.status = "PAID"
            order_dao.issue_date = datetime.now()

            session.add(order_dao)
            await session.commit()
            await session.refresh(order_dao)
            
            return order_dao