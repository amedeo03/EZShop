from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.database import AsyncSessionLocal
from app.models.DAO.product_dao import ProductDAO
from app.models.DTO.product_dto import ProductUpdateDTO
from app.models.errors.bad_request import BadRequestError
from app.models.errors.conflict_error import ConflictError
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
        barcode: str,
        price_per_unit: float,
        note: str,
        quantity: int,
        position: str,
    ) -> ProductDAO:
        """
        Create product.
        - Throws:
            - ConflictError if barcode exists or position is free
        """
        async with await self._get_session() as session:
            result = await session.execute(
                select(ProductDAO).filter(ProductDAO.barcode == barcode)
            )
            existing_products = result.scalars().all()

            throw_conflict_if_found(
                existing_products,
                lambda _: True,
                f"Product with barcode '{barcode}' already exists",
            )

            result = await session.execute(
                select(ProductDAO).filter(ProductDAO.position == position)
            )
            existing_products = result.scalars().all()

            throw_conflict_if_found(
                existing_products,
                lambda _: True,
                f"Product in position'{position}' already exists. Change it!",
            )

            product = ProductDAO(
                description=description,
                barcode=barcode,
                price_per_unit=price_per_unit,
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
                select(ProductDAO).filter(ProductDAO.barcode == barcode)
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

    async def update_product_position(
        self, product_id: int, position: str
    ) -> ProductDAO:
        """
        Update the position of a product.
        - Parameters: product_id (int), position (str)
        - Returns: Result of the operation as BooleanResponseDTO
        - Throws:
            - ConflictError if the specified position is not free
            - NotFoundError if the product id doesn't exist
        """
        async with await self._get_session() as session:
            product_db = await session.get(ProductDAO, product_id)
            if not product_db:
                raise NotFoundError(f"Product with id '{product_id}' not found")

            result_conflict = await session.execute(
                select(ProductDAO).filter(ProductDAO.position == position)
            )
            result_conflict = result_conflict.scalars().all()
            if result_conflict:
                raise ConflictError(
                    f"Product in position'{position}' already exists. Change it!"
                )

            product_db.position = position
            await session.commit()
            await session.refresh(product_db)
            return product_db

    async def update_product_quantity(
        self, product_id: int, quantity: int
    ) -> ProductDAO:
        """
        Update the quantity of a product.
        - Parameters: product_id (int), quantity (int)
        - Returns: Result of the operation as BooleanResponseDTO
        - Throws:
            - NotFoundError if the product id doesn't exist
            - BadRequestError if quantity to subtract is insufficient
        """
        async with await self._get_session() as session:
            product_db = await session.get(ProductDAO, product_id)
            if not product_db:
                raise NotFoundError(f"Product with id '{product_id}' not found")

            if quantity < 0 and product_db.quantity < abs(quantity):
                raise BadRequestError(
                    f"Insufficient quantity: in stock {product_db.quantity}"
                )

            product_db.quantity += quantity
            await session.commit()
            await session.refresh(product_db)
            return product_db

    async def update_product(
        self,
        product_update_dto: ProductUpdateDTO,
        product_id: int = None,
    ) -> ProductDAO:
        """
        Update product information.
        - Raises:
            - NotFoundError if not found or ConflictError if the new barcode exists
            - ConflictError if barcode already exists
        """

        if product_update_dto.position is not None:
            await self.update_product_position(product_id, product_update_dto.position)

        async with await self._get_session() as session:
            db_product = await session.get(ProductDAO, product_id)
            if not db_product:
                raise NotFoundError(f"Product with {product_id} not found.")

            product_to_update = product_update_dto.model_dump(exclude_unset=True)

            result_conflict = await session.execute(
                select(ProductDAO).filter(
                    ProductDAO.barcode == product_to_update["barcode"]
                )
            )
            if result_conflict.scalars().first():
                raise ConflictError(
                    f"Barcode '{product_to_update['barcode']}' already in use."
                )

            for key, value in product_to_update.items():
                setattr(db_product, key, value)

            await session.commit()
            await session.refresh(db_product)
            return db_product
