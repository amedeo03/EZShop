from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func
from sqlalchemy.orm import selectinload

from app.database.database import AsyncSessionLocal
from app.models.DAO.return_transaction_dao import ReturnTransactionDAO
from app.models.DAO.returned_product_dao import ReturnedProductDAO
from app.models.DTO.boolean_response_dto import BooleanResponseDTO
from app.models.errors.invalid_state_error import InvalidStateError
from app.models.errors.notfound_error import NotFoundError
from app.utils import find_or_throw_not_found, throw_conflict_if_found
from app.models.return_status_type import ReturnStatus

class ReturnRepository:

    def __init__(self, session: Optional[AsyncSession] = None):
        self._session = session

    async def _get_session(self) -> AsyncSession:
        return self._session or AsyncSessionLocal()

    async def create_return_transaction(
        self,
        sale_id: int
    ) -> ReturnTransactionDAO:
        """
        Create new Return Transaction.
        - Throws:
            - ConflictError ?
        """
        async with await self._get_session() as session:
            
            return_transaction = ReturnTransactionDAO(
                sale_id = sale_id,
                status=ReturnStatus.OPEN, 
                created_at=func.now(),
                lines=[],
            )

            session.add(return_transaction)
            await session.commit()
            await session.refresh(return_transaction)
            return return_transaction

    async def list_returns(self) -> list[ReturnTransactionDAO]:
        """
        List all Return Transactions.
        - Returns: list of ReturnTransactionDAO
        """
        async with await self._get_session() as session:
            result = await session.execute(
                select(ReturnTransactionDAO).options(selectinload(ReturnTransactionDAO.lines))
            )
            returns = list(result.scalars())
            return find_or_throw_not_found(
                [returns] if returns else [],
                lambda _: True,
                f"There is no return present in the database",
            )
            
    async def get_return_by_id(self, return_id: int) -> ReturnTransactionDAO | None:
        """
        Get return by id or throw NotFoundError if not found
        """
        async with await self._get_session() as session:
            return_transaction = await session.execute(
                select(ReturnTransactionDAO)
                .filter(ReturnTransactionDAO.id == return_id)
                .options(selectinload(ReturnTransactionDAO.lines))
            )
            return_transaction = return_transaction.scalars().first()
            return find_or_throw_not_found(
                [return_transaction] if return_transaction else [],
                lambda _: True,
                f"Return with id '{return_id}' not found",
            )

    async def delete_return(self, return_id: int) -> BooleanResponseDTO:
        async with await self._get_session() as session:
            return_transaction = await session.execute(
                select(ReturnTransactionDAO)
                .filter(ReturnTransactionDAO.id == return_id))

            return_transaction = return_transaction.scalar()
            if return_transaction is None:
                raise NotFoundError("sale with id {return_id} not found")

            await session.delete(return_transaction)
            await session.commit()

            return BooleanResponseDTO(success=True)
        
    async def list_returns_for_sale_id(self, sale_id: int) -> list[ReturnTransactionDAO]:
        """
        List all Return Transactions for a given sale ID.
        - Returns: list of ReturnTransactionDAO
        """
        async with await self._get_session() as session:
            result = await session.execute(
                select(ReturnTransactionDAO)
                .filter(ReturnTransactionDAO.sale_id == sale_id)
                .options(selectinload(ReturnTransactionDAO.lines))
            )
            returns = list(result.scalars())
            return find_or_throw_not_found(
                [returns] if returns else [],
                lambda _: True,
                f"There is no return present in the database for sale id '{sale_id}'",
            )
            
    async def attach_product_to_return_transaction(
        self,
        return_id: int,
        barcode: str,
        amount: int
    ) -> ReturnedProductDAO:
        """
        Attach a product to a return transaction.
        - Throws:
            - ConflictError ?
        """
        async with await self._get_session() as session:
            
            returned_item = ReturnedProductDAO(
                return_id = return_id,
                barcode = barcode,
                amount = amount
            )

            session.add(returned_item)
            await session.commit()
            await session.refresh(returned_item)
            return returned_item
        
    