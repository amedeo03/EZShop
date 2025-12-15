from fastapi import HTTPException

from app.repositories.accounting_repository import AccountingRepository


class AccountingController:

    def __init__(self):
        self.repo = AccountingRepository()

    async def get_balance(self) -> float:
        """
        Get the current balance from the repository.
        """
        return await self.repo.get_balance()

    async def set_balance(self, amount: float) -> float:
        """
        Set the balance to a specific amount.
        """
        if amount < 0:
            # According to Swagger: must return 421 for negative values
            raise HTTPException(status_code=421, detail="Balance cannot be negative.")

        return await self.repo.set_balance(amount)

    async def reset_balance(self) -> float:
        """
        Reset the system balance to zero.
        """
        # Reset implies setting the balance explicitly to 0.0
        return await self.repo.set_balance(0.0)
