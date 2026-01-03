from unittest.mock import AsyncMock, MagicMock

import pytest

from app.models.DAO.accounting_dao import AccountingDAO
from app.repositories.accounting_repository import AccountingRepository


@pytest.fixture
def mock_session():
    """Async context manager"""
    # Used for async with await self._get_session() as session
    session = AsyncMock()
    session.__aenter__.return_value = session
    return session


@pytest.fixture
def repo(mock_session):
    """Injected Accounting repository"""
    return AccountingRepository(session=mock_session)


@pytest.mark.asyncio
class TestAccountingRepository:

    @pytest.mark.parametrize(
        "db_balance, expected_balance",
        [
            (AccountingDAO(balance=1500.0), 1500.0),  # Existing record on db
            (None, 0.0),  # Record never found
        ],
    )
    async def test_get_balance_set_or_zero(
        self, repo, mock_session, db_balance, expected_balance
    ):
        mock_result = MagicMock()
        mock_session.execute.return_value = mock_result
        mock_result.scalars.return_value.first.return_value = db_balance

        balance = await repo.get_balance()

        assert balance == expected_balance
        mock_session.execute.assert_called_once()

    async def test_set_balance_update_existing(self, repo, mock_session):
        existing_dao = AccountingDAO(balance=100.0)
        mock_result = MagicMock()
        mock_session.execute.return_value = mock_result
        mock_result.scalars.return_value.first.return_value = existing_dao

        result = await repo.set_balance(500.0)

        assert result is True
        assert existing_dao.balance == 500.0
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once_with(existing_dao)

    async def test_set_balance_create_new(self, repo, mock_session):
        mock_result = MagicMock()
        mock_session.execute.return_value = mock_result
        mock_result.scalars.return_value.first.return_value = None
        mock_session.add = MagicMock()

        result = await repo.set_balance(250.0)

        assert result is True
        mock_session.add.assert_called_once()
        added_obj = mock_session.add.call_args[0][0]
        assert isinstance(added_obj, AccountingDAO)
        assert added_obj.balance == 250.0
        mock_session.commit.assert_called_once()

    async def test_reset_balance(self, repo, mock_session):
        existing_dao = AccountingDAO(balance=999.0)
        mock_result = MagicMock()
        mock_session.execute.return_value = mock_result
        mock_result.scalars.return_value.first.return_value = existing_dao

        await repo.reset_balance()

        assert existing_dao.balance == 0.0
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once_with(existing_dao)
