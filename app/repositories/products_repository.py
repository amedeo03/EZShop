from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.database import AsyncSessionLocal
from app.models.DAO.product_dao import ProductDAO
from app.models.errors.notfound_error import NotFoundError
from app.utils import find_or_throw_not_found, throw_conflict_if_found


class ProductsRepository:

    def __init__(self, session: Optional[AsyncSession] = None):
        self._session = session

    async def _get_session(self) -> AsyncSession:
        return self._session or AsyncSessionLocal()

    async def list_products(self) -> list[ProductDAO]:
        """Get all products
        - Returns: ProductDAO from database
        """
        async with await self._get_session() as session:
            result = await session.execute(select(ProductDAO))
            return result.scalars().all()

    async def create_product(
        self,
        description: str,
        productCode: str,
        pricePerUnit: float,
        note: str,
        quantity: int,
        position: str,
    ) -> ProductDAO:
        """
        Create product or throw ConflictError if productCode exists
        """
        async with await self._get_session() as session:
            result = await session.execute(
                select(ProductDAO).filter(ProductDAO.productCode == productCode)
            )
            existing_products = result.scalars().all()

            throw_conflict_if_found(
                existing_products,
                lambda _: True,
                f"Product with productCode '{productCode}' already exists",
            )

            product = ProductDAO(
                description=description,
                productCode=productCode,
                pricePerUnit=pricePerUnit,
                note=note,
                quantity=quantity,
                position=position,
            )
            session.add(product)
            await session.commit()
            await session.refresh(product)
            return product

    async def get_product(self, product_id: int) -> ProductDAO | None:
        """
        Get product by id or throw NotFoundError if not found
        """
        async with await self._get_session() as session:
            product = await session.get(ProductDAO, product_id)
            return find_or_throw_not_found(
                [product] if product else [],
                lambda _: True,
                f"Product with id '{product_id}' not found",
            )

    async def get_product_by_barcode(self, barcode: str) -> ProductDAO:
        """
        Get product by barcode or throw NotFoundError if not found
        """
        async with await self._get_session() as session:
            product = await session.execute(
                select(ProductDAO).filter(ProductDAO.productCode == barcode)
            )
            product = product.scalars().all()
            return find_or_throw_not_found(
                product, lambda _: True, f"Product with barcode '{barcode}' not found"
            )

    async def get_product_by_description(self, description: str) -> list[ProductDAO]:
        """
        Get product by description or throw NotFoundError if not found
        """
        async with await self._get_session() as session:
            result = await session.execute(
                select(ProductDAO).filter(
                    ProductDAO.description.ilike(f"%{description}%")
                )
            )
            return result.scalars().all()

    async def update_product(
        self,
        description: str,
        productCode: str,
        pricePerUnit: float,
        note: str,
        quantity: int,
        position: str,
        product_id: int,
    ) -> ProductDAO:
        """
        Update product information.
        - Raises:
            - NotFoundError if not found or ConflictError if the new productCode exists
            - ConflictError if barcode already exists
        """
        async with await self._get_session() as session:
            db_product = await session.get(ProductDAO, product_id)
            if not db_product:
                raise NotFoundError(f"Product with {product_id} not found.")

            result_conflict = await session.execute(
                select(ProductDAO).filter(ProductDAO.productCode == productCode)
            )
            conflicting_barcode = result_conflict.scalars().all()
            throw_conflict_if_found(
                conflicting_barcode,
                lambda _: True,
                f"Barcode '{productCode}' already in use.",
            )

            db_product.description = description
            db_product.pricePerUnit = pricePerUnit
            db_product.note = note
            db_product.quantity = quantity
            db_product.position = position

            await session.commit()
            await session.refresh(db_product)
            return db_product
