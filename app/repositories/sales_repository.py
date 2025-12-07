from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.database import AsyncSessionLocal
from app.models.errors.notfound_error import NotFoundError
from app.utils import find_or_throw_not_found, throw_conflict_if_found


class SalesRepository:

    def __init__(self, session: Optional[AsyncSession] = None):
        self._session = session

    async def _get_session(self) -> AsyncSession:
        return self._session or AsyncSessionLocal()

    async def list_sales(self) -> list[SaleDAO]:
        """
        Description
        """
        async with await self._get_session() as session:
            result = await session.execute(select(SaleDAO))
            return result.scalars().all()