from unittest.mock import AsyncMock, MagicMock

import pytest
import pytest_asyncio

from app.controllers.accounting_controller import AccountingController
from app.models.DAO.accounting_dao import AccountingDAO
from app.models.DTO.boolean_response_dto import BooleanResponseDTO
from app.models.errors.balance_error import BalanceError


@pytest_asyncio.fixture
async def mock_session():
    session = AsyncMock()
    session.__aenter__.return_value = session
    return session


@pytest_asyncio.fixture
async def controller(mock_session):
    accounting_controller = AccountingController()

    async def side_effect():
        return mock_session

    accounting_controller.repo._get_session = side_effect
    return accounting_controller


@pytest.mark.asyncio
class TestAccountingController:

    async def test_get_balance(self, controller, mock_session):
        existing_dao = AccountingDAO(balance=250.0)
        mock_result = MagicMock()
        mock_session.execute.return_value = mock_result
        mock_result.scalars.return_value.first.return_value = existing_dao

        balance = await controller.get_balance()

        assert balance == 250.0

    @pytest.mark.parametrize(
        "amount, expected_error",
        [
            (100, None),
            (-25, BalanceError),
        ],
    )
    async def test_set_balance(self, controller, mock_session, amount, expected_error):
        existing_dao = AccountingDAO(balance=0.0)
        mock_result = MagicMock()
        mock_session.execute.return_value = mock_result
        mock_result.scalars.return_value.first.return_value = existing_dao

        if expected_error:
            with pytest.raises(BalanceError):
                await controller.set_balance(amount)
        else:
            response = await controller.set_balance(amount)
            assert response.success is True
            assert existing_dao.balance == 100.0

    async def test_reset_balance(self, controller, mock_session):
        existing_dao = AccountingDAO(balance=500.0)
        mock_result = MagicMock()
        mock_session.execute.return_value = mock_result
        mock_result.scalars.return_value.first.return_value = existing_dao

        await controller.reset_balance()

        assert existing_dao.balance == 0.0
        mock_session.commit.assert_called()
