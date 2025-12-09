from typing import Optional, List
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.database import AsyncSessionLocal
from app.models.DAO.order_dao import OrderDAO
from app.models.DAO.system_dao import SystemInfoDAO
from app.models.errors.notfound_error import NotFoundError
from app.models.errors.balance_error import BalanceError
from app.models.errors.app_error import AppError # For generic 400/420 errors

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
        """
        Create a new order in the database.
        """
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
        """
        Get all orders from the database.
        """
        async with await self._get_session() as session:
            result = await session.execute(select(OrderDAO))
            return result.scalars().all()
        
    async def pay_order(self, order_id: int) -> bool:
        async with await self._get_session() as session:
            # Get the Order
            order = await session.get(OrderDAO, order_id)
            if not order:
                raise NotFoundError(f"Order with id {order_id} not found")

            # Check Status (Must be ISSUED)
            if order.status != "ISSUED":
                 # Using generic AppError or BadRequest for invalid state
                raise AppError(420, "Order was not Issued", "InvalidStateError")

            # Calculate Cost
            cost = order.quantity * order.price_per_unit

            # Get System Balance
            result = await session.execute(select(SystemInfoDAO))
            system_info = result.scalars().first()
            
            # If system info doesn't exist, we assume 0 balance or create it
            if not system_info:
                raise BalanceError("System balance information not found")

            # Check Funds
            if system_info.balance < cost:
                raise BalanceError("Insufficient balance for the operation")

            # Execute Payment
            system_info.balance -= cost
            order.status = "PAID"
            
            await session.commit()
            return True