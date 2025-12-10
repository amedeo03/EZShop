from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database.database import AsyncSessionLocal
from app.models.DAO.sale_dao import SaleDAO
from app.models.DAO.sold_product_dao import SoldProductDAO
from app.utils import find_or_throw_not_found


class SalesRepository:

    def __init__(self, session: Optional[AsyncSession] = None):
        self._session = session

    async def _get_session(self) -> AsyncSession:
        return self._session or AsyncSessionLocal()

    async def create_sale(self) -> SaleDAO:
        async with await self._get_session() as session:
            sale = SaleDAO(
                status="OPEN",
                discount_rate=0.0,
                lines=[],
            )

            session.add(sale)
            await session.commit()
            await session.refresh(sale)
            return sale

    async def list_sales(self) -> List[SaleDAO] | None:
        """
        Get all sales present in the database
        - Returns: List[SaleDAO]
        """
        async with await self._get_session() as session:
            result = await session.execute(
                select(SaleDAO).options(selectinload(SaleDAO.lines))
            )
            sales = list(result.scalars())
            return find_or_throw_not_found(
                [sales] if sales else [],
                lambda _: True,
                f"There is no sale present in the database",
            )

    async def get_sale_by_id(self, sale_id: int) -> SaleDAO | None:
        """
        Get product by id or throw NotFoundError if not found
        """
        async with await self._get_session() as session:
            sales = await session.execute(
                select(SaleDAO)
                .filter(SaleDAO.id == sale_id)
                .options(selectinload(SaleDAO.lines))
            )
            sales = sales.scalars().first()
            return find_or_throw_not_found(
                [sales] if sales else [],
                lambda _: True,
                f"Sale with id '{sale_id}' not found",
            )
