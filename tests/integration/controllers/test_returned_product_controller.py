import pytest
import pytest_asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.controllers.returned_product_controller import ReturnedProductController
from app.database.database import Base
from app.models.DAO.returned_product_dao import ReturnedProductDAO
from app.models.errors.bad_request import BadRequestError
from app.models.errors.conflict_error import ConflictError
from app.models.errors.invalid_state_error import InvalidStateError
from app.models.errors.notfound_error import NotFoundError
from app.repositories.returned_products_repository import ReturnedProductsRepository

DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture
async def db_session():
    engine = create_async_engine(DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    SessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)

    async with SessionLocal() as session:
        yield session

    await engine.dispose()


@pytest.mark.asyncio
class TestReturnedProductController:

    async def test_create_returned_product(self, db_session):
        """Test creating a returned product"""
        repo = ReturnedProductsRepository(session=db_session)
        controller = ReturnedProductController()
        controller.repo = repo

        # Act
        result = await controller.create_returned_product(
            id=1,
            return_id=10,
            product_barcode="1234567890128",
            quantity=5,
            price_per_unit=9.99,
        )

        # Assert
        assert result.id == 1
        assert result.return_id == 10
        assert result.product_barcode == "1234567890128"
        assert result.quantity == 5
        assert result.price_per_unit == 9.99

        # Verify in database
        db_result = await db_session.execute(
            select(ReturnedProductDAO).where(ReturnedProductDAO.id == 1)
        )
        created = db_result.scalars().first()
        assert created is not None
        assert created.product_barcode == "1234567890128"

    @pytest.mark.parametrize(
        "id, return_id, barcode, quantity, price, expected_exception",
        [
            (-1, 10, "1234567890128", 5, 9.99, BadRequestError),  # Negative id
            (1, -10, "1234567890128", 5, 9.99, BadRequestError),  # Negative return_id
            (1, 10, "123", 5, 9.99, BadRequestError),  # Invalid barcode
            (1, 10, "1234567890128", -5, 9.99, BadRequestError),  # Negative quantity
            (1, 10, "1234567890128", 5, -9.99, BadRequestError),  # Negative price
            (1, 10, "ABC1234567890", 5, 9.99, BadRequestError),  # Barcode with letters
        ],
    )
    async def test_create_returned_product_validation(
        self, db_session, id, return_id, barcode, quantity, price, expected_exception
    ):
        """Test input validation for create_returned_product"""
        repo = ReturnedProductsRepository(session=db_session)
        controller = ReturnedProductController()
        controller.repo = repo

        # Act & Assert
        with pytest.raises(expected_exception):
            await controller.create_returned_product(
                id=id,
                return_id=return_id,
                product_barcode=barcode,
                quantity=quantity,
                price_per_unit=price,
            )

    async def test_create_returned_product_duplicate(self, db_session):
        """Test creating duplicate returned product raises ConflictError"""
        repo = ReturnedProductsRepository(session=db_session)
        controller = ReturnedProductController()
        controller.repo = repo

        # Create first product
        await controller.create_returned_product(
            id=1,
            return_id=10,
            product_barcode="1234567890128",
            quantity=5,
            price_per_unit=9.99,
        )

        # Try to create duplicate
        with pytest.raises(ConflictError):
            await controller.create_returned_product(
                id=2,
                return_id=10,
                product_barcode="1234567890128",
                quantity=3,
                price_per_unit=9.99,
            )

    async def test_edit_quantity_decrease(self, db_session):
        """Test decreasing quantity of returned product"""
        repo = ReturnedProductsRepository(session=db_session)
        controller = ReturnedProductController()
        controller.repo = repo

        # Create product
        await controller.create_returned_product(
            id=1,
            return_id=10,
            product_barcode="1234567890128",
            quantity=10,
            price_per_unit=9.99,
        )

        # Edit quantity
        result = await controller.edit_quantity_of_returned_product(
            return_id=10, barcode="1234567890128", amount=3
        )

        # Assert
        assert result.quantity == 7

        # Verify in database
        db_result = await db_session.execute(
            select(ReturnedProductDAO).where(ReturnedProductDAO.id == 1)
        )
        updated = db_result.scalars().first()
        assert updated.quantity == 7

    async def test_edit_quantity_to_zero_deletes(self, db_session):
        """Test decreasing quantity to zero deletes the product"""
        repo = ReturnedProductsRepository(session=db_session)
        controller = ReturnedProductController()
        controller.repo = repo

        # Create product
        await controller.create_returned_product(
            id=1,
            return_id=10,
            product_barcode="1234567890128",
            quantity=5,
            price_per_unit=9.99,
        )

        # Edit quantity to zero
        await controller.edit_quantity_of_returned_product(
            return_id=10, barcode="1234567890128", amount=5
        )

        # Verify deleted from database
        db_result = await db_session.execute(
            select(ReturnedProductDAO).where(ReturnedProductDAO.id == 1)
        )
        deleted = db_result.scalars().first()
        assert deleted is None

    @pytest.mark.parametrize(
        "return_id, barcode, amount, expected_exception",
        [
            (-1, "1234567890128", 1, BadRequestError),  # Negative return_id
            (10, "123", 1, BadRequestError),  # Invalid barcode
            (10, "1234567890128", -1, BadRequestError),  # Negative amount
            (10, "1234567890127", 1, BadRequestError),  # Invalid barcode GTIN
            (10, "", 1, BadRequestError),  # Empty barcode
            (10, "ABC1234567890", 1, BadRequestError),  # Barcode with letters
        ],
    )
    async def test_edit_quantity_validation(
        self, db_session, return_id, barcode, amount, expected_exception
    ):
        """Test input validation for edit_quantity_of_returned_product"""
        repo = ReturnedProductsRepository(session=db_session)
        controller = ReturnedProductController()
        controller.repo = repo

        # Act & Assert
        with pytest.raises(expected_exception):
            await controller.edit_quantity_of_returned_product(
                return_id=return_id, barcode=barcode, amount=amount
            )

    async def test_edit_quantity_not_found(self, db_session):
        """Test editing non-existent product raises NotFoundError"""
        repo = ReturnedProductsRepository(session=db_session)
        controller = ReturnedProductController()
        controller.repo = repo

        # Act & Assert
        with pytest.raises(NotFoundError):
            await controller.edit_quantity_of_returned_product(
                return_id=999, barcode="1234567890128", amount=1
            )

    async def test_edit_quantity_insufficient(self, db_session):
        """Test removing more than available raises InvalidStateError"""
        repo = ReturnedProductsRepository(session=db_session)
        controller = ReturnedProductController()
        controller.repo = repo

        # Create product with quantity 3
        await controller.create_returned_product(
            id=1,
            return_id=10,
            product_barcode="1234567890128",
            quantity=3,
            price_per_unit=9.99,
        )

        # Try to remove 10
        with pytest.raises(InvalidStateError):
            await controller.edit_quantity_of_returned_product(
                return_id=10, barcode="1234567890128", amount=10
            )

    async def test_get_by_id(self, db_session):
        """Test getting returned product by id"""
        repo = ReturnedProductsRepository(session=db_session)
        controller = ReturnedProductController()
        controller.repo = repo

        # Create product
        await controller.create_returned_product(
            id=1,
            return_id=10,
            product_barcode="1234567890128",
            quantity=5,
            price_per_unit=9.99,
        )

        # Get by id
        result = await controller.get_returned_products_by_id(product_id=1)

        # Assert
        assert result.id == 1
        assert result.product_barcode == "1234567890128"
        assert result.quantity == 5

    async def test_get_by_id_not_found(self, db_session):
        """Test getting by id when not found raises NotFoundError"""
        repo = ReturnedProductsRepository(session=db_session)
        controller = ReturnedProductController()
        controller.repo = repo

        # Act & Assert
        with pytest.raises(NotFoundError):
            await controller.get_returned_products_by_id(product_id=999)

    async def test_get_by_id_validation(self, db_session):
        """Test validation for get_returned_products_by_id"""
        repo = ReturnedProductsRepository(session=db_session)
        controller = ReturnedProductController()
        controller.repo = repo

        # Act & Assert - negative id
        with pytest.raises(BadRequestError):
            await controller.get_returned_products_by_id(product_id=-1)

    async def test_get_by_barcode(self, db_session):
        """Test getting returned products by barcode"""
        repo = ReturnedProductsRepository(session=db_session)
        controller = ReturnedProductController()
        controller.repo = repo

        # Create returned product
        await controller.create_returned_product(
            id=1,
            return_id=10,
            product_barcode="1502234567865",
            quantity=5,
            price_per_unit=9.99,
        )

        # Get by barcode
        results = await controller.get_returned_product_by_barcode(
            product_barcode="1502234567865"
        )

        # Assert
        assert len(results) == 1
        assert results[0].product_barcode == "1502234567865"

    async def test_get_by_barcode_not_found(self, db_session):
        """Test getting by barcode when not found raises NotFoundError"""
        repo = ReturnedProductsRepository(session=db_session)
        controller = ReturnedProductController()
        controller.repo = repo

        # Act & Assert - using valid GTIN barcode that doesn't exist
        with pytest.raises(NotFoundError):
            await controller.get_returned_product_by_barcode(
                product_barcode="1234567890128"
            )

    @pytest.mark.parametrize(
        "barcode, expected_exception",
        [
            ("", BadRequestError),  # Empty barcode
            ("123", BadRequestError),  # Too short
            ("12345678912345689", BadRequestError),  # Too long
            ("ABC1234567890", BadRequestError),  # Contains letters
        ],
    )
    async def test_get_by_barcode_validation(
        self, db_session, barcode, expected_exception
    ):
        """Test validation for get_returned_product_by_barcode"""
        repo = ReturnedProductsRepository(session=db_session)
        controller = ReturnedProductController()
        controller.repo = repo

        # Act & Assert
        with pytest.raises(expected_exception):
            await controller.get_returned_product_by_barcode(product_barcode=barcode)
