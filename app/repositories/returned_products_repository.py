from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.database import AsyncSessionLocal
from app.models.DAO.returned_product_dao import ReturnedProductDAO
from app.models.DTO.boolean_response_dto import BooleanResponseDTO
from app.models.errors.bad_request import BadRequestError
from app.models.errors.conflict_error import ConflictError
from app.models.errors.notfound_error import NotFoundError
from app.utils import find_or_throw_not_found, throw_conflict_if_found


class ReturnedProductsRepository:

    def __init__(self, session: Optional[AsyncSession] = None):
        self._session = session

    async def _get_session(self) -> AsyncSession:
        return self._session or AsyncSessionLocal()

    async def create_returned_product(
        self,
        id: int,
        return_id: int,
        product_barcode: str,
        quantity: int,
        price_per_unit: float,
    ) -> ReturnedProductDAO:
        """
        Create returned product.
        - Throws:
            - ConflictError if an existing product with the same id/barcode is already associated to the same sale
        """
        async with await self._get_session() as session:
            result = await session.execute(
                select(ReturnedProductDAO).filter(
                    (ReturnedProductDAO.product_barcode == product_barcode)
                    & (ReturnedProductDAO.return_id == return_id)
                )
            )

            existing_product = result.scalar_one_or_none()

            if existing_product is not None:
                raise ConflictError(
                    "ReturnedProduct with id '{id}' already exists in return transaction '{return_id}'"
                )

            returned_product = ReturnedProductDAO(
                id=id,
                return_id=return_id,
                product_barcode=product_barcode,
                quantity=quantity,
                price_per_unit=price_per_unit,
            )

            session.add(returned_product)
            await session.commit()
            await session.refresh(returned_product)
            return returned_product