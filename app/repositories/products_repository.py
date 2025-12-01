from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.DAO.product_dao import ProductDAO
from app.utils import throw_conflict_if_found, find_or_throw_not_found
from app.database.database import AsyncSessionLocal
from typing import Optional


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

    async def create_product(self, description: str, productCode: str, pricePerUnit: float, note: str, quantity: int, position: str) -> ProductDAO:
        """
        Create product or throw ConflictError if productCode exists
        """
        async with await self._get_session() as session:
            result = await session.execute(select(ProductDAO).filter(ProductDAO.productCode == productCode))
            existing_products = result.scalars().all()

            throw_conflict_if_found(
                existing_products,
                lambda _: True,
                f"Product with productCode '{productCode}' already exists"
            )

            product = ProductDAO(description=description, productCode=productCode, pricePerUnit=pricePerUnit, note=note, quantity=quantity, position=position)
            session.add(product)
            await session.commit()
            await session.refresh(product)
            return product
