from unittest.mock import AsyncMock, MagicMock

import pytest

from app.models.DAO.return_transaction_dao import ReturnTransactionDAO  # noqa
from app.models.DAO.returned_product_dao import ReturnedProductDAO
from app.models.errors.conflict_error import ConflictError
from app.models.errors.invalid_state_error import InvalidStateError
from app.models.errors.notfound_error import NotFoundError
from app.repositories.returned_products_repository import ReturnedProductsRepository


@pytest.fixture
def mock_session():
    """Async context manager for mocked session"""
    session = AsyncMock()
    session.__aenter__.return_value = session
    return session


@pytest.fixture
def repo(mock_session):
    """Injected ReturnedProducts repository with mocked session"""
    return ReturnedProductsRepository(session=mock_session)


@pytest.mark.asyncio
class TestReturnedProductsRepository:

    async def test_create_returned_product(self, repo, mock_session):
        """Test creating a returned product"""
        # Arrange
        mock_result = MagicMock()
        mock_session.execute.return_value = mock_result
        mock_session.add = MagicMock()
        mock_result.scalar_one_or_none.return_value = None

        # Act
        await repo.create_returned_product(
            id=1,
            return_id=10,
            product_barcode="1234567890128",
            quantity=5,
            price_per_unit=9.99,
        )

        # Assert
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once()

    async def test_create_returned_product_duplicate(self, repo, mock_session):
        """Test creating a returned product that already exists"""
        # Arrange
        existing_product = MagicMock(spec=ReturnedProductDAO)
        existing_product.id = 1
        existing_product.return_id = 10
        existing_product.product_barcode = "1234567890128"

        mock_result = MagicMock()
        mock_session.execute.return_value = mock_result
        mock_result.scalar_one_or_none.return_value = existing_product

        # Act & Assert
        with pytest.raises(ConflictError) as exc_info:
            await repo.create_returned_product(
                id=1,
                return_id=10,
                product_barcode="1234567890128",
                quantity=3,
                price_per_unit=9.99,
            )

        assert "already exists" in str(exc_info.value).lower()
        mock_session.add.assert_not_called()

    async def test_edit_quantity_decrease(self, repo, mock_session):
        """Test decreasing quantity of a returned product"""
        # Arrange
        returned_product = MagicMock(spec=ReturnedProductDAO)
        returned_product.quantity = 10

        mock_result = MagicMock()
        mock_session.execute.return_value = mock_result
        mock_result.scalar_one_or_none.return_value = returned_product

        # Act
        result = await repo.edit_quantity_of_returned_product(
            return_id=10, barcode="1234567890128", amount=3
        )

        # Assert
        assert result.quantity == 7
        mock_session.commit.assert_called()
        mock_session.refresh.assert_called_with(returned_product)
        mock_session.delete.assert_not_called()

    async def test_edit_quantity_to_zero(self, repo, mock_session):
        """Test decreasing quantity to zero deletes the product"""
        # Arrange
        returned_product = MagicMock(spec=ReturnedProductDAO)
        returned_product.quantity = 5

        mock_result = MagicMock()
        mock_session.execute.return_value = mock_result
        mock_result.scalar_one_or_none.return_value = returned_product

        # Act
        await repo.edit_quantity_of_returned_product(
            return_id=10, barcode="1234567890128", amount=5
        )

        # Assert
        assert returned_product.quantity == 0
        mock_session.delete.assert_called_once_with(returned_product)
        assert mock_session.commit.call_count == 2

    async def test_edit_quantity_not_found(self, repo, mock_session):
        """Test editing quantity of non-existent returned product"""
        # Arrange
        mock_result = MagicMock()
        mock_session.execute.return_value = mock_result
        mock_result.scalar_one_or_none.return_value = None

        # Act & Assert
        with pytest.raises(NotFoundError) as exc_info:
            await repo.edit_quantity_of_returned_product(
                return_id=999, barcode="1234567890128", amount=1
            )

        assert "not found" in str(exc_info.value).lower()
        mock_session.delete.assert_not_called()

    async def test_edit_quantity_insufficient(self, repo, mock_session):
        """Test removing more quantity than available"""
        # Arrange
        returned_product = MagicMock(spec=ReturnedProductDAO)
        returned_product.quantity = 3

        mock_result = MagicMock()
        mock_session.execute.return_value = mock_result
        mock_result.scalar_one_or_none.return_value = returned_product

        # Act & Assert
        with pytest.raises(InvalidStateError) as exc_info:
            await repo.edit_quantity_of_returned_product(
                return_id=10, barcode="1234567890128", amount=10
            )

        assert "cannot delete" in str(exc_info.value).lower()
        mock_session.delete.assert_not_called()

    async def test_get_by_id(self, repo, mock_session):
        """Test getting a returned product by id"""
        # Arrange
        returned_product = MagicMock(spec=ReturnedProductDAO)

        mock_result = MagicMock()
        mock_session.execute.return_value = mock_result
        mock_result.scalars.return_value.first.return_value = returned_product

        # Act
        result = await repo.get_returned_products_by_id(product_id=1)

        # Assert
        assert result == returned_product
        mock_session.execute.assert_called_once()

    async def test_get_by_id_not_found(self, repo, mock_session):
        """Test getting a returned product by id when not found"""
        # Arrange
        mock_result = MagicMock()
        mock_session.execute.return_value = mock_result
        mock_result.scalars.return_value.first.return_value = None

        # Act & Assert
        with pytest.raises(NotFoundError) as exc_info:
            await repo.get_returned_products_by_id(product_id=999)

        assert "never returned" in str(exc_info.value).lower()

    @pytest.mark.parametrize(
        "db_return, expected_exception",
        [
            ([MagicMock(spec=ReturnedProductDAO, product_barcode="1502234567865")], None),
            ([], NotFoundError),
        ],
    )
    async def test_get_returned_products_by_barcode(
        self, repo, mock_session, db_return, expected_exception
    ):
        """Test getting returned products by barcode"""
        # Arrange
        mock_result = MagicMock()
        mock_session.execute.return_value = mock_result
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = db_return
        mock_result.scalars.return_value = mock_scalars

        if expected_exception:
            # Act & Assert - Not found case
            with pytest.raises(expected_exception):
                await repo.get_returned_product_by_barcode(barcode="0901234123452")
        else:
            # Act - Found case
            result = await repo.get_returned_product_by_barcode("1502234567865")

            # Assert
            assert isinstance(result, list)
            assert len(result) == 1
            assert result[0].product_barcode == "1502234567865"
            mock_session.execute.assert_called_once()