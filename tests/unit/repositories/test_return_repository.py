from unittest.mock import AsyncMock, MagicMock

import pytest

from app.models.DAO.return_transaction_dao import ReturnTransactionDAO
from app.models.DTO.boolean_response_dto import BooleanResponseDTO
from app.models.errors.invalid_state_error import InvalidStateError
from app.models.errors.notfound_error import NotFoundError
from app.models.return_status_type import ReturnStatus
from app.repositories.return_repository import ReturnRepository


@pytest.fixture
def mock_session():
    """Async context manager for mocked session"""
    session = AsyncMock()
    session.__aenter__.return_value = session
    return session


@pytest.fixture
def repo(mock_session):
    """Injected Return repository with mocked session"""
    return ReturnRepository(session=mock_session)


@pytest.mark.asyncio
class TestReturnRepository:

    async def test_create_return_transaction(self, repo, mock_session):
        """Test creating a return transaction"""
        # Arrange
        mock_session.add = MagicMock()
        sale_id = 1

        # Act
        await repo.create_return_transaction(sale_id=sale_id)

        # Assert
        mock_session.add.assert_called_once()
        added_obj = mock_session.add.call_args[0][0]
        assert isinstance(added_obj, ReturnTransactionDAO)
        assert added_obj.sale_id == sale_id
        assert added_obj.status == ReturnStatus.OPEN
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once()

    async def test_list_returns_with_results(self, repo, mock_session):
        """Test listing all returns when returns exist"""
        # Arrange
        mock_return_1 = ReturnTransactionDAO(
            id=1, sale_id=1, status=ReturnStatus.OPEN, lines=[]
        )
        mock_return_2 = ReturnTransactionDAO(
            id=2, sale_id=2, status=ReturnStatus.CLOSED, lines=[]
        )

        mock_result = MagicMock()
        mock_session.execute.return_value = mock_result
        mock_result.scalars.return_value = [mock_return_1, mock_return_2]

        # Act
        returns = await repo.list_returns()

        # Assert
        assert len(returns) == 2
        assert returns[0].id == 1
        assert returns[1].id == 2
        mock_session.execute.assert_called_once()

    async def test_list_returns_empty_raises_not_found(self, repo, mock_session):
        """Test listing returns when database is empty"""
        # Arrange
        mock_result = MagicMock()
        mock_session.execute.return_value = mock_result
        mock_result.scalars.return_value = []

        # Act & Assert
        with pytest.raises(NotFoundError) as exc_info:
            await repo.list_returns()

        assert "no return present" in str(exc_info.value).lower()

    async def test_get_return_by_id_success(self, repo, mock_session):
        """Test getting a return by valid ID"""
        # Arrange
        return_id = 1
        mock_return = ReturnTransactionDAO(
            id=return_id, sale_id=1, status=ReturnStatus.OPEN, lines=[]
        )

        mock_result = MagicMock()
        mock_session.execute.return_value = mock_result
        mock_result.scalars.return_value.first.return_value = mock_return

        # Act
        result = await repo.get_return_by_id(return_id)

        # Assert
        assert result.id == return_id
        assert result.sale_id == 1
        assert result.status == ReturnStatus.OPEN
        mock_session.execute.assert_called_once()

    async def test_get_return_by_id_not_found(self, repo, mock_session):
        """Test getting a return with non-existent ID"""
        # Arrange
        mock_result = MagicMock()
        mock_session.execute.return_value = mock_result
        mock_result.scalars.return_value.first.return_value = None

        # Act & Assert
        with pytest.raises(NotFoundError) as exc_info:
            await repo.get_return_by_id(999999)

        assert "not found" in str(exc_info.value).lower()

    async def test_delete_return_success(self, repo, mock_session):
        """Test deleting a return transaction"""
        # Arrange
        return_id = 1
        mock_return = ReturnTransactionDAO(
            id=return_id, sale_id=1, status=ReturnStatus.OPEN, lines=[]
        )

        mock_result = MagicMock()
        mock_session.execute.return_value = mock_result
        mock_result.scalar.return_value = mock_return

        # Act
        result = await repo.delete_return(return_id)

        # Assert
        assert isinstance(result, BooleanResponseDTO)
        assert result.success is True
        mock_session.delete.assert_called_once_with(mock_return)
        mock_session.commit.assert_called_once()

    async def test_delete_return_not_found(self, repo, mock_session):
        """Test deleting a non-existent return"""
        # Arrange
        mock_result = MagicMock()
        mock_session.execute.return_value = mock_result
        mock_result.scalar.return_value = None

        # Act & Assert
        with pytest.raises(NotFoundError):
            await repo.delete_return(999999)

        mock_session.delete.assert_not_called()
        mock_session.commit.assert_not_called()

    async def test_list_returns_for_sale_id_success(self, repo, mock_session):
        """Test listing returns for a specific sale"""
        # Arrange
        sale_id = 1
        mock_return_1 = ReturnTransactionDAO(
            id=1, sale_id=sale_id, status=ReturnStatus.OPEN, lines=[]
        )
        mock_return_2 = ReturnTransactionDAO(
            id=2, sale_id=sale_id, status=ReturnStatus.CLOSED, lines=[]
        )

        mock_result = MagicMock()
        mock_session.execute.return_value = mock_result
        mock_result.scalars.return_value = [mock_return_1, mock_return_2]

        # Act
        returns = await repo.list_returns_for_sale_id(sale_id)

        # Assert
        assert len(returns) == 2
        assert all(r.sale_id == sale_id for r in returns)
        mock_session.execute.assert_called_once()

    async def test_close_return_transaction_not_found(self, repo, mock_session):
        """Test closing a non-existent return raises NotFoundError"""
        # Arrange
        mock_result = MagicMock()
        mock_session.execute.return_value = mock_result
        mock_result.scalar_one_or_none.return_value = None

        # Act & Assert
        with pytest.raises(NotFoundError):
            await repo.close_return_transaction(999999)

    async def test_reimburse_return_not_closed_raises_invalid_state(
        self, repo, mock_session
    ):
        """Test reimbursing an open return raises InvalidStateError"""
        # Arrange
        mock_return = ReturnTransactionDAO(
            id=1, sale_id=1, status=ReturnStatus.OPEN, lines=[]
        )

        mock_result = MagicMock()
        mock_session.execute.return_value = mock_result
        mock_result.scalar_one_or_none.return_value = mock_return

        # Act & Assert
        with pytest.raises(InvalidStateError):
            await repo.reimburse_return_transaction(1)

    async def test_reimburse_return_not_found(self, repo, mock_session):
        """Test reimbursing a non-existent return"""
        # Arrange
        mock_result = MagicMock()
        mock_session.execute.return_value = mock_result
        mock_result.scalar_one_or_none.return_value = None

        # Act & Assert
        with pytest.raises(NotFoundError):
            await repo.reimburse_return_transaction(999999)
