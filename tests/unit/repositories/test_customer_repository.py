"""
Unit tests for the Customer Repository.

Tests cover all CRUD operations and card management functionality using mocked AsyncSession.
"""

from unittest.mock import AsyncMock, MagicMock
import pytest

from app.models.DAO.customer_dao import CustomerDAO
from app.models.DAO.card_dao import CardDAO
from app.models.errors.notfound_error import NotFoundError
from app.models.errors.conflict_error import ConflictError
from app.models.errors.customer_card_error import CustomerCardError
from app.repositories.customer_repository import CustomerRepository


@pytest.fixture
def mock_session():
    """Mock AsyncSession for testing."""
    session = AsyncMock()
    session.__aenter__.return_value = session
    return session


@pytest.fixture
def repo(mock_session):
    """Injected Customer repository with mocked session."""
    return CustomerRepository(session=mock_session)


@pytest.mark.asyncio
class TestCustomerRepository:
    """Test cases for CustomerRepository."""

    # ===== CREATE CUSTOMER TESTS =====
    @pytest.mark.parametrize(
        "name, cardId",
        [("John Doe", "1234567890")],
    )
    async def test_create_customer_with_new_card(self, repo, mock_session, name, cardId):
        """Test creating a customer with a new card."""
        
        card_dao = CardDAO(cardId=cardId, points=0)
        
        # Mock get_card_by_id to return a card
        mock_result = MagicMock()
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_result.scalars.return_value.first.return_value = None  # No conflict
        
        # Mock session.get to return the card
        mock_session.get = AsyncMock(return_value=card_dao)
        
        result = await repo.create_customer(name, cardId, 0)
        
        assert isinstance(result, CustomerDAO)
        assert result.name == name
        assert result.cardId == cardId
        
        # Verify session.add was called
        mock_session.add.assert_called_once()
        # Verify session.commit and refresh were called
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once()
        
    @pytest.mark.parametrize(
        "name, cardId",
        [("John Doe", None)],
    )
    async def test_create_customer_without_card(self, repo, mock_session, name, cardId):
        """Test creating a customer without a card."""
        # Mock session.get to return None (no card found)
        mock_session.get = AsyncMock(return_value=None)

        result = await repo.create_customer(name, cardId, 0)

        assert isinstance(result, CustomerDAO)
        assert result.name == name
        assert result.cardId == cardId
        
        # Verify session.add was called
        mock_session.add.assert_called_once()
        # Verify session.commit and refresh were called
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once()

    @pytest.mark.parametrize(
        "name_1, name_2, cardId",
        [("John Doe", "Jane Smith", "1234567890")],
    )
    async def test_create_customer_with_card_already_attached(self, repo, mock_session, name_1, name_2, cardId):
        """Test creating a customer when card is already attached to another customer."""
        existing_customer = CustomerDAO(id=99, name=name_1, cardId=cardId)
        card_dao = CardDAO(cardId=cardId, points=50)
        
        # Mock get_card_by_id to return a card
        mock_result = MagicMock()
        mock_session.execute.return_value = mock_result
        # First call: check for card existence, Second call: check for conflict
        mock_result.scalars.return_value.first.side_effect = [card_dao, existing_customer]
        
        result = await repo.create_customer(name_2, cardId, 0)
        
        assert isinstance(result, CustomerDAO)
        assert result.name == name_2
        assert result.cardId == None # Because the card is already attached to another customer
        
        # Should still add customer but without the card
        mock_session.add.assert_called_once()
        

    # ===== LIST CUSTOMER TESTS =====
    @pytest.mark.parametrize(
        "name_1, name_2, cardId_1, cardId_2",
        [("John Doe", "Jane Smith", "1234567890", "0987654321")],
    )
    async def test_list_customer_with_customers(self, repo, mock_session, name_1, name_2, cardId_1, cardId_2):
        """Test listing all customers."""
        customers = [
            CustomerDAO(id=1, name=name_1, cardId=cardId_1),
            CustomerDAO(id=2, name=name_2, cardId=cardId_2),
        ]
        
        mock_result = MagicMock()
        mock_session.execute.return_value = mock_result
        mock_result.scalars.return_value.all.return_value = customers
        
        result = await repo.list_customer()
        
        assert result == customers
        assert len(result) == 2
        mock_session.execute.assert_called_once()

    async def test_list_customer_empty(self, repo, mock_session):
        """Test listing customers when no customers exist."""
        mock_result = MagicMock()
        mock_session.execute.return_value = mock_result
        mock_result.scalars.return_value.all.return_value = []
        
        result = await repo.list_customer()
        
        assert result == []
        mock_session.execute.assert_called_once()

    # ===== GET CUSTOMER TESTS =====
    
    @pytest.mark.parametrize(
        "name_1, cardId_1",
        [("John Doe", "1234567890")],
    )
    async def test_get_customer_success(self, repo, mock_session, name_1, cardId_1):
        """Test retrieving an existing customer."""
        customer_dao = CustomerDAO(id=1, name=name_1, cardId=cardId_1)
        card_dao = CardDAO(cardId=cardId_1, points=0)
        customer_dao.card = card_dao
        
        mock_result = MagicMock()
        mock_session.execute.return_value = mock_result
        mock_result.scalars.return_value.first.return_value = customer_dao
        
        result = await repo.get_customer(1)
        
        assert result == customer_dao
        assert result.id == 1
        assert result.name == name_1
        mock_session.execute.assert_called_once()

    async def test_get_customer_not_found(self, repo, mock_session):
        """Test retrieving a non-existent customer."""
        mock_result = MagicMock()
        mock_session.execute.return_value = mock_result
        mock_result.scalars.return_value.first.return_value = None
        
        with pytest.raises(NotFoundError):
            await repo.get_customer(999)

    # ===== UPDATE CUSTOMER ONLY NAME TESTS =====
    @pytest.mark.parametrize(
        "name_1,updated_name, cardId_1",
        [("John Doe", "John Update", "1234567890")],
    )
    async def test_update_customer_only_name_success(self, repo, mock_session, name_1, updated_name, cardId_1):
        """Test updating only the customer name."""
        existing_customer = CustomerDAO(id=1, name=name_1, cardId=cardId_1)
        
        mock_session.get.return_value = existing_customer
        
        result = await repo.update_customer_only_name(1, updated_name)
        
        assert result.name == updated_name
        assert result.id == 1
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once_with(existing_customer)

    async def test_update_customer_only_name_not_found(self, repo, mock_session):
        """Test updating a non-existent customer."""
        mock_session.get.return_value = None
        
        result = await repo.update_customer_only_name(999, "New Name")
        
        assert result is None
        mock_session.commit.assert_not_called()

    # ===== UPDATE CUSTOMER WITH CARD TESTS =====
    @pytest.mark.parametrize(
        "name_1, cardId_1",
        [("John Doe", "1234567890")],
    )
    async def test_update_customer_with_card_success(self, repo, mock_session, name_1, cardId_1):
        """Test updating customer with a new card."""
        existing_customer = CustomerDAO(id=1, name=name_1, cardId=None)
        new_card = CardDAO(cardId=cardId_1, points=100)
        
        mock_session.get.side_effect = [existing_customer, new_card]
        
        mock_result = MagicMock()
        mock_session.execute.return_value = mock_result
        mock_result.scalars.return_value.first.return_value = None  # No conflict
        
        result = await repo.update_customer(1, name_1, cardId_1, 0)
        
        assert result.name == name_1
        assert result.cardId == cardId_1
        assert new_card.points == 100
        mock_session.commit.assert_called_once()

    @pytest.mark.parametrize(
        "name_1",
        [("John Doe")],
    )
    async def test_update_customer_card_not_found(self, repo, mock_session, name_1):
        """Test updating customer with a non-existent card."""
        existing_customer = CustomerDAO(id=1, name=name_1, cardId=None)
        
        mock_session.get.side_effect = [existing_customer, None]  # Card not found
        
        with pytest.raises(NotFoundError, match="Card not found"):
            await repo.update_customer(1, name_1, "9999999999", 50)
    
    @pytest.mark.parametrize(
        "name_1, name_2, cardID",
        [("John Doe", "Jane Smith", "9876543210")],
    )
    async def test_update_customer_card_already_attached(self, repo, mock_session, name_1, name_2, cardID):
        """Test updating customer with a card already attached to another customer."""
        existing_customer = CustomerDAO(id=1, name=name_1, cardId=None)
        other_customer = CustomerDAO(id=2, name=name_2, cardId=cardID)
        new_card = CardDAO(cardId=cardID, points=50)
        
        mock_session.get.side_effect = [existing_customer, new_card]
        
        mock_result = MagicMock()
        mock_session.execute.return_value = mock_result
        mock_result.scalars.return_value.first.return_value = other_customer  # Card already attached
        
        with pytest.raises(ConflictError, match="already attached to a customer"):
            await repo.update_customer(1, name_1, cardID, 50)

    async def test_update_customer_not_found(self, repo, mock_session):
        """Test updating a non-existent customer."""
        mock_session.get.return_value = None
        
        result = await repo.update_customer(999, "New Name", None, 0)
        
        assert result is None
        mock_session.commit.assert_not_called()

    # ===== DELETE CUSTOMER TESTS =====
    @pytest.mark.parametrize(
        "name_1",
        [("John Doe")],
    )
    async def test_delete_customer_success(self, repo, mock_session, name_1):
        """Test deleting an existing customer."""
        customer_dao = CustomerDAO(id=1, name=name_1, cardId=None)
        mock_session.get.return_value = customer_dao
        
        result = await repo.delete_customer(1)
        
        assert result is True
        mock_session.delete.assert_called_once_with(customer_dao)
        mock_session.commit.assert_called_once()

    async def test_delete_customer_not_found(self, repo, mock_session):
        """Test deleting a non-existent customer."""
        mock_session.get.return_value = None
        
        with pytest.raises(NotFoundError, match="not found"):
            await repo.delete_customer(999)

    # ===== CREATE CARD TESTS =====

    async def test_create_card_first_card(self, repo, mock_session):
        """Test creating the first card."""
        mock_result = MagicMock()
        mock_session.execute.return_value = mock_result
        mock_result.scalars.return_value.first.return_value = None  # No cards exist
        
        result = await repo.create_card()
        
        assert len(result.cardId) == 10
        assert result.points == 0
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()

    async def test_create_card_increments_id(self, repo, mock_session):
        """Test creating multiple cards with incrementing IDs."""
        existing_card = CardDAO(cardId="0000000005", points=0)
        
        mock_result = MagicMock()
        mock_session.execute.return_value = mock_result
        mock_result.scalars.return_value.first.return_value = existing_card
        
        result = await repo.create_card()
        
        assert result.cardId == "0000000006"
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()

    # ===== ATTACH CARD TESTS =====
    @pytest.mark.parametrize(
        "name_1, cardId_1",
        [("John Doe", "1234567890")],
    )
    async def test_attach_card_success(self, repo, mock_session, name_1, cardId_1):
        """Test attaching a card to a customer."""
        customer_dao = CustomerDAO(id=1, name=name_1, cardId=None)
        card_dao = CardDAO(cardId=cardId_1, points=50)
        
        # Mock session.get to return card
        mock_session.get = AsyncMock(return_value=card_dao)
        
        # Mock execute for customer lookup and conflict check
        mock_result = MagicMock()
        mock_session.execute = AsyncMock(return_value=mock_result)
        # First execute returns customer, second execute returns None (no conflict)
        mock_result.scalars.return_value.first.side_effect = [customer_dao, None]
        
        result = await repo.attach_card("1", cardId_1)
        
        assert result is not None
        assert result.cardId == cardId_1
        mock_session.commit.assert_called_once()

    @pytest.mark.parametrize(
        "name_1",
        [("John Doe")],
    )
    async def test_attach_card_card_not_found(self, repo, mock_session, name_1):
        """Test attaching a non-existent card."""
        customer_dao = CustomerDAO(id=1, name=name_1, cardId=None)
        
        # Mock both get (for card lookup) and execute (for customer lookup)
        mock_session.get = AsyncMock(side_effect=[None, customer_dao])  # Card not found
        
        mock_result = MagicMock()
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_result.scalars.return_value.first.return_value = customer_dao
        
        result = await repo.attach_card("1", "9999999999")
        
        assert result is None
        mock_session.commit.assert_not_called()

    @pytest.mark.parametrize(
        "cardID",
        [("1234567890")],
    )
    async def test_attach_card_customer_not_found(self, repo, mock_session, cardID):
        """Test attaching a card to a non-existent customer."""
        card_dao = CardDAO(cardId=cardID, points=50)
        
        # Mock both get (for card lookup, customer lookup) and execute
        mock_session.get = AsyncMock(side_effect=[card_dao, None])  # Customer not found
        
        mock_result = MagicMock()
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_result.scalars.return_value.first.return_value = None
        
        result = await repo.attach_card("999", cardID)
        
        assert result is None
        mock_session.commit.assert_not_called()

    @pytest.mark.parametrize(
        "name_1, name_2, cardID",
        [("John Doe", "Jane Smith", "1234567890")],
    )
    async def test_attach_card_already_attached(self, repo, mock_session, name_1, name_2, cardID):
        """Test attaching a card that's already attached to another customer."""
        customer_dao = CustomerDAO(id=1, name=name_1, cardId=None)
        card_dao = CardDAO(cardId=cardID, points=50)
        other_customer = CustomerDAO(id=2, name=name_2, cardId=cardID)
        
        mock_session.get.side_effect = [card_dao, customer_dao]
        
        mock_result = MagicMock()
        mock_session.execute.return_value = mock_result
        mock_result.scalars.return_value.first.return_value = other_customer  # Card already attached
        
        with pytest.raises(ConflictError, match="already attached to a customer"):
            await repo.attach_card("1", cardID)

    # ===== MODIFY POINTS TESTS =====
    @pytest.mark.parametrize(
        "cardID, points, added_points",
        [("1234567890", 50, 25)],
    )
    async def test_modify_point_increase(self, repo, mock_session, cardID, points, added_points):
        """Test increasing points on a card."""
        card_dao = CardDAO(cardId=cardID, points=points)
        mock_session.get.return_value = card_dao
        
        result = await repo.modify_point(cardID, added_points)
        
        assert result.points == points + added_points
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once_with(card_dao)

    @pytest.mark.parametrize(
        "cardID, points, subtracted_points",
        [("1234567890", 50, 30)],
    )
    async def test_modify_point_decrease(self, repo, mock_session, cardID, points, subtracted_points):
        """Test decreasing points on a card."""
        card_dao = CardDAO(cardId=cardID, points=points)
        mock_session.get.return_value = card_dao

        result = await repo.modify_point(cardID, -subtracted_points)
        
        assert result.points == points - subtracted_points
        mock_session.commit.assert_called_once()

    @pytest.mark.parametrize(
        "cardID, points, subtracted_points",
        [("1234567890", 50, 300)],
    )
    async def test_modify_point_insufficient_points(self, repo, mock_session, cardID, points, subtracted_points):
        """Test decreasing points below zero raises error."""
        card_dao = CardDAO(cardId=cardID, points=points)
        mock_session.get.return_value = card_dao
        
        with pytest.raises(CustomerCardError, match="Insufficient points"):
            await repo.modify_point(cardID, -subtracted_points)
            
            
    async def test_modify_point_card_not_found(self, repo, mock_session):
        """Test modifying points on a non-existent card."""
        mock_session.get.return_value = None
        
        result = await repo.modify_point("9999999999", 50)
        
        assert result is None
        mock_session.commit.assert_not_called()

    # ===== GET CARD BY ID TESTS =====
    @pytest.mark.parametrize(
        "cardID",
        [("1234567890")],
    )
    async def test_get_card_by_id_success(self, repo, mock_session, cardID):
        """Test retrieving a card by ID."""
        card_dao = CardDAO(cardId=cardID, points=50)
        mock_session.get.return_value = card_dao
        
        result = await repo.get_card_by_id(cardID)
        
        assert result == card_dao
        assert result.cardId == cardID
        mock_session.get.assert_called_once_with(CardDAO, cardID)
        
    async def test_get_card_by_id_not_found(self, repo, mock_session):
        """Test retrieving a non-existent card."""
        mock_session.get.return_value = None
        
        result = await repo.get_card_by_id("9999999999")
        
        assert result is None
        mock_session.get.assert_called_once()

    async def test_get_card_by_id_none_card_id(self, repo, mock_session):
        """Test retrieving a card with None as ID."""
        result = await repo.get_card_by_id(None)
        
        assert result is None
