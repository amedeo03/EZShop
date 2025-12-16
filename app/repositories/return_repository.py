from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func

from app.database.database import AsyncSessionLocal
from app.models.DAO.return_transaction_dao import ReturnTransactionDAO
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
