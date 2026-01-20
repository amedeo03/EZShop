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
from app.models.errors.bad_request import BadRequestError
from app.models.errors.customer_card_error import CustomerCardError
from app.repositories.customer_repository import CustomerRepository


@pytest.fixture
def mock_session():
    """Mock AsyncSession for testing."""
    session = AsyncMock()
    session.__aenter__.return_value = session
    # session.add is a synchronous call in SQLAlchemy; make it a non-async mock
    session.add = MagicMock()
    # session.delete, commit and refresh are awaited in the repository, keep them async
    session.delete = AsyncMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
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
        "name, cardId, points",
        [("John Doe", "1234567890", 0),
         ("Jane Smith", None, 0),
         ("John Doe", "1234567890", 100)],
    )
    async def test_create_customer(self, repo, mock_session, name, cardId, points):
        """Test creating a customer with a new card."""
        
        # Mock get_card_by_id to return a card
        mock_result = MagicMock()
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_result.scalars.return_value.first.return_value = None  # No conflict
        
        if cardId is not None:
            card_dao = CardDAO(cardId=cardId, points=0)
            # Mock session.get to return the card
            mock_session.get = AsyncMock(return_value=card_dao)
        
        result = await repo.create_customer(name, cardId, points)
        
        assert isinstance(result, CustomerDAO)
        assert result.name == name
        assert result.cardId == cardId

        # Verify session.add was called
        mock_session.add.assert_called_once()
        # Verify session.commit and refresh were called
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once()
        
 

    @pytest.mark.parametrize(
        "customer_1, customer_2, card, expected_error",
        [
            (
                CustomerDAO(id=1, 
                      name="John Doe", 
                      cardId="0000000001"
                      ), 
          CustomerDAO(id=2, 
                      name="Jane Smith", 
                      cardId="0000000001"
                      ), 
          CardDAO(cardId="0000000001", points=50),
          BadRequestError
          )
          ],
    )
    async def test_create_customer_with_card_already_attached(self, repo, mock_session, customer_1, customer_2, card, expected_error):
        """Test creating a customer when card is already attached to another customer."""
        #existing_customer = CustomerDAO(id=99, name=name_1, cardId=cardId)
        #card_dao = CardDAO(cardId=cardId, points=50)
        
        # Mock get_card_by_id to return a card
        mock_result = MagicMock()
        mock_session.execute.return_value = mock_result
        # First call: check for card existence, Second call: check for conflict
        mock_result.scalars.return_value.first.side_effect = [card, customer_1]
        
        if expected_error:
            with pytest.raises(expected_error):
                await repo.create_customer(customer_2.name, card.cardId, 0)
            
        
            
        

    # ===== LIST CUSTOMER TESTS =====
    @pytest.mark.parametrize(
        "name_1, name_2, cardId_1, cardId_2",
        [("John Doe", "Jane Smith", "1234567890", "0987654321")],
    )
    async def test_list_customer(self, repo, mock_session, name_1, name_2, cardId_1, cardId_2):
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
        "customer, new_card, customer_id, expected_error",
        [
            (
                CustomerDAO(id=1, name="John Doe", cardId="0000000001"),
                CardDAO(cardId="0000000001", points=100),
                1,
                None
             ),
            (
                CustomerDAO(id=1, name="John Doe", cardId="0000000001"),
                CardDAO(cardId="0000000001", points=100),
                999,
                NotFoundError
             )
],
    )
    async def test_get_customer(self, repo, mock_session, customer, new_card, customer_id, expected_error):
        """Test retrieving an existing customer."""

        customer.card = new_card
        
        mock_result = MagicMock()
        mock_session.execute.return_value = mock_result
        
        # Return customer only if customer_id matches, otherwise None
        if customer_id == customer.id:
            mock_result.scalars.return_value.first.return_value = customer
        else:
            mock_result.scalars.return_value.first.return_value = None
        
        if expected_error:
            with pytest.raises(expected_error):
                await repo.get_customer(customer_id)
        else:
            result = await repo.get_customer(customer_id)
            
            assert result == customer
            assert result.id == customer_id
            assert result.card.cardId == new_card.cardId
            assert result.card.points == new_card.points
            mock_session.execute.assert_called_once()


    # ===== UPDATE CUSTOMER ONLY NAME TESTS =====
    @pytest.mark.parametrize(
        "customer, updated_name, not_found",
        [
            (CustomerDAO(id=1, name="John Doe", cardId="1234567890"),
             "John Update",
             True
             ),
            (CustomerDAO(id=1, name="John Doe", cardId="1234567890"),
             "John Update",
             False
             )
            ],
    )
    async def test_update_customer_only_name(self, repo, mock_session, customer, updated_name, not_found):
        """Test updating only the customer name."""
        
        if not_found:
            mock_session.get.return_value = customer
            
            result = await repo.update_customer_only_name(1, updated_name)
        
            assert result.name == updated_name
            assert result.id == 1
            mock_session.commit.assert_called_once()
            mock_session.refresh.assert_called_once_with(customer)
        else:
            mock_session.get.return_value = None
        
            result = await repo.update_customer_only_name(999, updated_name)
            
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

    async def test_create_card(self, repo, mock_session):
        """Test creating the first card."""
        mock_result = MagicMock()
        mock_session.execute.return_value = mock_result
        mock_result.scalars.return_value.first.return_value = None  # No cards exist
        
        result = await repo.create_card()
        
        assert len(result.cardId) == 10
        assert result.points == 0
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
        "cardID, orig_points, added_points, expected_exception",
        [("1234567890", 50, 25, None),
         ("1234567890", 50, -25, None),
         ("1234567890", 50, -100, CustomerCardError)],
    )
    async def test_modify_point(self, repo, mock_session, cardID, orig_points, added_points, expected_exception):
        """Test increasing points on a card."""
        card_dao = CardDAO(cardId=cardID, points=orig_points)
        mock_session.get.return_value = card_dao

        if expected_exception:
            with pytest.raises(expected_exception):
                await repo.modify_point(cardID, added_points)
        else:
            result = await repo.modify_point(cardID, added_points)

            assert result.points == orig_points + added_points
            mock_session.commit.assert_called_once()
            mock_session.refresh.assert_called_once_with(card_dao)

    
            
            
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


