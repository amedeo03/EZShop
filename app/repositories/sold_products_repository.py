from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.database import AsyncSessionLocal
from app.models.DAO.sold_product_dao import SoldProductDAO
from app.models.DTO.boolean_response_dto import BooleanResponseDTO
from app.models.errors.bad_request import BadRequestError
from app.models.errors.conflict_error import ConflictError
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
        """
        async with await self._get_session() as session:
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

    async def get_sold_product(self, product_id: int, sale_id: int) -> SoldProductDAO:
        """
        Get product by id and sale id or throw NotFoundError if not found
        """
        async with await self._get_session() as session:
            result = await session.execute(
                select(SoldProductDAO).filter(
                    (SoldProductDAO.id == product_id)
                    & (SoldProductDAO.sale_id == sale_id)
                )
            )
            products = result.scalar()
            if products is None:
                raise NotFoundError("No products with id '{product_id}' sold")
            else:
                return products

    async def get_sold_product_by_sale_barcode(
        self, sale_id: int, barcode: str
    ) -> SoldProductDAO:
        """
        Get product by barcode and sale id or throw NotFoundError if not found
        """
        async with await self._get_session() as session:
            result = await session.execute(
                select(SoldProductDAO).filter(
                    (SoldProductDAO.product_barcode == barcode)
                    & (SoldProductDAO.sale_id == sale_id)
                )
            )
            products = result.scalar()
            if products is None:
                raise NotFoundError("No products with id '{product_id}' sold")
            else:
                return products

    async def get_sold_product_by_id(self, product_id: int) -> list[SoldProductDAO]:
        """
        Get product(s) by id or throw NotFoundError if not found
        """
        async with await self._get_session() as session:
            result = await session.execute(
                select(SoldProductDAO).filter(SoldProductDAO.id == product_id)
            )
            products = list(result.scalars().all())
            return products

    async def edit_sold_product_quantity(
        self, id: int, sale_id: int, quantity: int
    ) -> BooleanResponseDTO:
        """
        Edit a given sold product quantity, delete it if the remaining quantity is zero
        Throw NotFoundError if not found
        """
        async with await self._get_session() as session:
            result = await session.execute(
                select(SoldProductDAO).filter(
                    (SoldProductDAO.id == id) & (SoldProductDAO.sale_id == sale_id)
                )
            )
            if result is None:
                raise NotFoundError("Sold product not found with the given IDs")
            sold_product: SoldProductDAO = result.scalar()

            if sold_product.quantity + quantity < 0:  # type: ignore
                raise BadRequestError(
                    "Quantity to be removed is higher than the one in the sale"
                )
            else:
                sold_product.quantity += quantity  # type: ignore
                await session.commit()
                await session.refresh(sold_product)

        return BooleanResponseDTO(success=True)

    async def edit_sold_product_discount(
        self, id: int, sale_id: int, discount_rate: float
    ) -> BooleanResponseDTO:
        """
        Edit a given sold product discount rate
        Throw NotFoundError if not found
        """
        async with await self._get_session() as session:
            result = await session.execute(
                select(SoldProductDAO).filter(
                    (SoldProductDAO.id == id) & (SoldProductDAO.sale_id == sale_id)
                )
            )

            if result is None:
                raise NotFoundError("Sold product not found with the given IDs")
            sold_product: SoldProductDAO = result.scalar()

            sold_product.discount_rate = discount_rate  # type: ignore
            await session.commit()
            await session.refresh(sold_product)

        return BooleanResponseDTO(success=True)

    async def remove_sold_product(self, sale_id: int, id: int):
        async with await self._get_session() as session:
            res = await session.execute(
                select(SoldProductDAO).filter(
                    (SoldProductDAO.id == id) & (SoldProductDAO.sale_id == sale_id)
                )
            )
            await session.delete(res.scalar())
            await session.commit()
