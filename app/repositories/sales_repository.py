import datetime
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database.database import AsyncSessionLocal
from app.models.DAO.sale_dao import SaleDAO
from app.models.DAO.sold_product_dao import SoldProductDAO
from app.models.DTO.boolean_response_dto import BooleanResponseDTO
from app.models.errors.invalid_state_error import InvalidStateError
from app.models.errors.notfound_error import NotFoundError
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

    async def list_sales(self) -> List[SaleDAO]:
        """
        Get all sales present in the database
        - Returns: List[SaleDAO]
        """
        async with await self._get_session() as session:
            result = await session.execute(
                select(SaleDAO).options(selectinload(SaleDAO.lines))
            )
            sales = list(result.scalars())
        return sales

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

    async def delete_sale(self, sale_id: int) -> BooleanResponseDTO:
        async with await self._get_session() as session:
            sale = await session.execute(select(SaleDAO).filter(SaleDAO.id == sale_id))

            sale = sale.scalar()
            if sale is None:
                raise NotFoundError("sale with id {sale_id} not found")

            await session.delete(sale)
            await session.commit()

            return BooleanResponseDTO(success=True)

    async def edit_sale_discount(
        self, sale_id: int, discount_rate: float
    ) -> BooleanResponseDTO:
        async with await self._get_session() as session:
            result = await session.execute(
                select(SaleDAO).filter(SaleDAO.id == sale_id)
            )

            sale = result.scalar()
            if sale is None:
                raise NotFoundError("Sale id {sale_id} not found")

            if sale.status != "OPEN":  # type: ignore
                raise InvalidStateError("Sale is not 'OPEN'")

            sale.discount_rate = discount_rate  # type: ignore
            await session.commit()
            await session.refresh(sale)

            return BooleanResponseDTO(success=True)

    async def edit_sale_status(
        self, sale_id: int, new_status: str
    ) -> BooleanResponseDTO:
        async with await self._get_session() as session:
            result = await session.execute(
                select(SaleDAO).filter(SaleDAO.id == sale_id)
            )

            sale = result.scalar()
            if sale is None:
                raise NotFoundError("Sale id {sale_id} not found")

            if new_status == "PENDING":
                if sale.status != "OPEN":  # type: ignore
                    raise InvalidStateError("Sale is not 'OPEN'")
                sale.closed_at = datetime.datetime.now(datetime.timezone.utc).replace(  # type: ignore
                    microsecond=0
                )

            if new_status == "PAID":
                if sale.status != "PENDING":  # type: ignore
                    raise InvalidStateError("Sale is not 'PENDING'")

            sale.status = new_status  # type: ignore
            await session.commit()
            await session.refresh(sale)

            return BooleanResponseDTO(success=True)
