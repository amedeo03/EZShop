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
        Retrieve the current system balance.
        Returns 0.0 if the register has not been initialized.
        """
        async with await self._get_session() as session:
            # Get System Info
            # We assume the first row in 'system_info' is the shop's balance
            result = await session.execute(select(AccountingDAO))
            system_info = result.scalars().first()

            # If system info doesn't exist, we assume 0 balance
            if not system_info:
                return 0.0
            
            return system_info.balance

    async def set_balance(self, new_balance: float) -> float:
        """
        Set the system balance to a specific amount.
        Creates the record if it does not exist.
        """
        async with await self._get_session() as session:
            # Get System Info
            result = await session.execute(select(AccountingDAO))
            system_info = result.scalars().first()

            if system_info:
                # Update existing record
                system_info.balance = new_balance
            else:
                # Create the missing record (Lazy Initialization)
                # This prevents "System balance information not found" errors
                system_info = AccountingDAO(balance=new_balance)
                session.add(system_info)

            # Commit changes and refresh object
            await session.commit()
            await session.refresh(system_info)
            
            return system_info.balance