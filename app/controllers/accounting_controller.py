from app.models.DTO.boolean_response_dto import BooleanResponseDTO
from app.models.errors.balance_error import BalanceError
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
            raise BalanceError("Balance cannot be negative.")

        if await self.repo.set_balance(amount):
            return BooleanResponseDTO(success=True)

    async def reset_balance(self) -> None:
        """
        Reset the system balance to 0
        """
        await self.repo.reset_balance()
