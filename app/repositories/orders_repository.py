from typing import Optional, List
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.database import AsyncSessionLocal
from app.models.DAO.order_dao import OrderDAO

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