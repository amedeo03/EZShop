from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.database import AsyncSessionLocal
from app.models.DAO.accounting_dao import AccountingDAO


class AccountingRepository:

    def __init__(self, session: Optional[AsyncSession] = None):
        self._session = session

    async def _get_session(self) -> AsyncSession:
        return self._session or AsyncSessionLocal()

    async def get_balance(self) -> float:
        """
        Retrieve the current balance.
        Returns 0.0 if the register has not been initialized.
        """
        async with await self._get_session() as session:
            balance_db = await session.execute(select(AccountingDAO))
            balance_db = balance_db.scalars().first()

            if not balance_db:
                return 0.0

            return balance_db.balance

    async def set_balance(self, new_balance: float) -> bool:
        """
        Set the system balance to a specific amount.
        Creates the record if it does not exist.
        """
        async with await self._get_session() as session:
            balance_db = await session.execute(select(AccountingDAO))
            balance_db = balance_db.scalars().first()

            if balance_db:
                balance_db.balance = new_balance
            else:
                balance_db = AccountingDAO(balance=new_balance)
                session.add(balance_db)

            await session.commit()
            await session.refresh(balance_db)
            return True

    async def reset_balance(self) -> None:
        """
        Reset the balance to 0.
        """
        async with await self._get_session() as session:
            balance_db = await session.execute(select(AccountingDAO))
            balance_db = balance_db.scalars().first()

            balance_db.balance = 0.0

            await session.commit()
            await session.refresh(balance_db)
