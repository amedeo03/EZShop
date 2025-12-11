from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.database import AsyncSessionLocal
from app.models.DAO.sold_product_dao import SoldProductDAO
from app.models.DTO.boolean_response_dto import BooleanResponseDTO
from app.models.errors.notfound_error import NotFoundError
from app.utils import find_or_throw_not_found, throw_conflict_if_found


class SoldProductsRepository:

    def __init__(self, session: Optional[AsyncSession] = None):
        self._session = session

    async def _get_session(self) -> AsyncSession:
        return self._session or AsyncSessionLocal()

    async def create_sold_product(
        self,
        id: int,
        sale_id: int,
        product_barcode: str,
        quantity: int,
        price_per_unit: float,
        discount_rate: float,
    ) -> SoldProductDAO:
        """
        Create sold product.
        - Throws:
            - ConflictError if an existing product with the same id/barcode is already associated to the same sale
        """
        async with await self._get_session() as session:
            result = await session.execute(
                select(SoldProductDAO).filter(
                    SoldProductDAO.product_barcode == product_barcode
                    and SoldProductDAO.sale_id == sale_id
                )
            )

            existing_products = list(result.scalars())

            throw_conflict_if_found(
                existing_products,
                lambda _: True,
                f"Product with barcode '{product_barcode}' already exists in sale {sale_id}",
            )

            result = await session.execute(
                select(SoldProductDAO).filter(
                    SoldProductDAO.id == id and SoldProductDAO.sale_id == sale_id
                )
            )

            existing_products = list(result.scalars())

            throw_conflict_if_found(
                existing_products,
                lambda _: True,
                f"Product with id '{id}' already exists in sale {sale_id}",
            )

            sold_product = SoldProductDAO(
                id=id,
                sale_id=sale_id,
                product_barcode=product_barcode,
                quantity=quantity,
                price_per_unit=price_per_unit,
                discount_rate=discount_rate,
            )

            session.add(sold_product)
            await session.commit()
            await session.refresh(sold_product)
            return sold_product

    async def get_sold_product_by_id(
        self, product_id: int
    ) -> list[SoldProductDAO] | None:
        """
        Get product(s) by id or throw NotFoundError if not found
        """
        async with await self._get_session() as session:
            result = await session.execute(
                select(SoldProductDAO).filter(SoldProductDAO.id == product_id)
            )

    async def get_sold_product_by_barcode(
        self, barcode: str
    ) -> list[SoldProductDAO] | None:
        """
        Get product(s) by barcode or throw NotFoundError if not found
        """
        async with await self._get_session() as session:
            result = await session.execute(
                select(SoldProductDAO).filter(SoldProductDAO.product_barcode == barcode)
            )

    async def delete_sold_product(self, id: int, sale_id: int) -> BooleanResponseDTO:
        """
        Delete a given sold product or throw NotFoundError if not found
        """
        async with await self._get_session() as session:
            result = await session.execute(
                select(SoldProductDAO).filter(
                    SoldProductDAO.id == id and SoldProductDAO.sale_id == sale_id
                )
            )
            if not result:
                raise NotFoundError("sold product not found")

            await session.delete(result.first())
            await session.commit()
            await session.refresh(result)

        return BooleanResponseDTO(success=True)
