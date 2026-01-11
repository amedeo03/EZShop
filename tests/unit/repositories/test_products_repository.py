from unittest.mock import AsyncMock, MagicMock

import pytest

from app.models.DTO.product_dto import ProductUpdateDTO
from app.models.errors.bad_request import BadRequestError
from app.models.errors.conflict_error import ConflictError
from app.models.errors.notfound_error import NotFoundError
from app.repositories.products_repository import ProductDAO, ProductsRepository


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
    return ProductsRepository(session=mock_session)


# Tests
class TestProductsRepository:
    @pytest.mark.parametrize(
        "product, outcome",
        [
            (
                ProductDAO(
                    description="coffee",
                    barcode="4006381333931",
                    price_per_unit=1.5,
                    note="",
                    quantity=50,
                    position="A-1-1",
                ),
                "success",
            ),
            (
                ProductDAO(  # barcode conflict
                    description="coffee",
                    barcode="9780201379624",
                    price_per_unit=1.5,
                    note="",
                    quantity=50,
                    position="A-1-1",
                ),
                "conflict",
            ),
            (
                ProductDAO(  # position conflict
                    description="coffee",
                    barcode="4006381333931",
                    price_per_unit=1.5,
                    note="",
                    quantity=50,
                    position="B-1-1",
                ),
                "conflict",
            ),
        ],
    )
    async def test_create_product(self, repo, mock_session, product, outcome):
        mock_result = MagicMock()
        mock_session.execute = AsyncMock(return_value=mock_result)

        # create another product to test conflicts
        existing_product = ProductDAO(
            description="milk",
            barcode="9780201379624",
            price_per_unit=1.5,
            note="",
            quantity=10,
            position="B-1-1",
        )

        if outcome == "success":
            mock_result.scalars.return_value.all.return_value = []
        elif outcome == "conflict":
            mock_result.scalars.return_value.all.return_value = [existing_product]

        if outcome == "success":
            result = await repo.create_product(
                product.description,
                product.barcode,
                product.price_per_unit,
                product.note,
                product.quantity,
                product.position,
            )

            assert isinstance(result, ProductDAO)
            assert result.description == product.description
            assert result.barcode == product.barcode
            assert result.price_per_unit == product.price_per_unit
            assert result.note == product.note
            assert result.quantity == product.quantity
            assert result.position == product.position

            mock_session.add.assert_called_once()
            mock_session.commit.assert_called_once()
            mock_session.refresh.assert_called_once()

        elif outcome == "conflict":
            with pytest.raises(ConflictError):
                await repo.create_product(
                    product.description,
                    product.barcode,
                    product.price_per_unit,
                    product.note,
                    product.quantity,
                    product.position,
                )

            mock_session.add.assert_not_called()
            mock_session.commit.assert_not_called()

    @pytest.mark.asyncio
    async def test_list_products(self, repo, mock_session):
        mock_result = MagicMock()
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_result.scalars.return_value.all.return_value = []

        product = ProductDAO(
            description="milk",
            barcode="9780201379624",
            price_per_unit=1.5,
            note="",
            quantity=10,
            position="B-1-1",
        )

        product_count: int = len(await repo.list_products())
        assert product_count == 0

        mock_result.scalars.return_value.all.return_value = [product, product, product]
        product_count: int = len(await repo.list_products())
        assert product_count == 3

    @pytest.mark.parametrize(
        "returned_product, outcome",
        [
            (
                ProductDAO(
                    id=1,
                    description="coffee",
                    barcode="4006381333931",
                    price_per_unit=1.5,
                    note="",
                    quantity=50,
                    position="A-1-1",
                ),
                "success",
            ),
            (
                None,
                "not_found",
            ),
        ],
    )
    async def test_get_product(self, repo, mock_session, returned_product, outcome):
        mock_session.get = AsyncMock(return_value=returned_product)

        if outcome == "success":
            result = await repo.get_product(1)

            assert isinstance(result, ProductDAO)
            assert result.id == 1  # type: ignore

            mock_session.get.assert_called_once_with(ProductDAO, 1)

        else:
            with pytest.raises(NotFoundError):
                await repo.get_product(1)

            mock_session.get.assert_called_once_with(ProductDAO, 1)

    @pytest.mark.parametrize(
        "db_result, outcome",
        [
            ([ProductDAO(barcode="123")], "success"),
            ([], "not_found"),
        ],
    )
    async def test_get_product_by_barcode(self, repo, mock_session, db_result, outcome):
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = db_result
        mock_session.execute = AsyncMock(return_value=mock_result)

        if outcome == "success":
            product = await repo.get_product_by_barcode("123")
            assert product.barcode == "123"
        else:
            with pytest.raises(NotFoundError):
                await repo.get_product_by_barcode("123")

        mock_session.execute.assert_called_once()

    @pytest.mark.parametrize(
        "db_result",
        [
            [],
            [ProductDAO(description="coffee")],
        ],
    )
    async def test_get_product_by_description(self, repo, mock_session, db_result):
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = db_result
        mock_session.execute = AsyncMock(return_value=mock_result)

        result = await repo.get_product_by_description("coffee")

        assert result == db_result
        mock_session.execute.assert_called_once()

    @pytest.mark.parametrize(
        "product_exists, conflict_exists, outcome",
        [
            (False, False, "not_found"),
            (True, True, "conflict"),
            (True, False, "success"),
        ],
    )
    async def test_update_product_position(
        self, repo, mock_session, product_exists, conflict_exists, outcome
    ):
        product = ProductDAO(position="A-1-1")

        mock_session.get = AsyncMock(return_value=product if product_exists else None)

        conflict_result = MagicMock()
        conflict_result.scalars.return_value.all.return_value = (
            [ProductDAO()] if conflict_exists else []
        )

        mock_session.execute = AsyncMock(return_value=conflict_result)

        if outcome == "success":
            result = await repo.update_product_position(1, "B-1-1")
            assert result.position == "B-1-1"
            mock_session.commit.assert_called_once()
            mock_session.refresh.assert_called_once()
        elif outcome == "conflict":
            with pytest.raises(ConflictError):
                await repo.update_product_position(1, "B-1-1")
        else:
            with pytest.raises(NotFoundError):
                await repo.update_product_position(1, "B-1-1")

    @pytest.mark.parametrize(
        "initial_qty, delta, outcome",
        [
            (None, 5, "not_found"),
            (5, -10, "bad_request"),
            (5, 3, "success"),
        ],
    )
    async def test_update_product_quantity(
        self, repo, mock_session, initial_qty, delta, outcome
    ):
        product = ProductDAO(quantity=initial_qty) if initial_qty is not None else None

        mock_session.get = AsyncMock(return_value=product)

        if outcome == "success":
            result = await repo.update_product_quantity(1, delta)
            assert result.quantity == initial_qty + delta
            mock_session.commit.assert_called_once()
            mock_session.refresh.assert_called_once()
        elif outcome == "bad_request":
            with pytest.raises(BadRequestError):
                await repo.update_product_quantity(1, delta)
        else:
            with pytest.raises(NotFoundError):
                await repo.update_product_quantity(1, delta)

    @pytest.mark.parametrize(
        "db_exists, barcode_conflict, outcome",
        [
            (False, False, "not_found"),
            (True, True, "conflict"),
            (True, False, "success"),
        ],
    )
    async def test_update_product(
        self, repo, mock_session, db_exists, barcode_conflict, outcome
    ):
        dto = ProductUpdateDTO(barcode="NEW123", description="updated")

        product = ProductDAO(barcode="OLD123")

        mock_session.get = AsyncMock(return_value=product if db_exists else None)

        conflict_result = MagicMock()
        conflict_result.scalars.return_value.first.return_value = (
            ProductDAO() if barcode_conflict else None
        )

        mock_session.execute = AsyncMock(return_value=conflict_result)

        if outcome == "success":
            result = await repo.update_product(dto, product_id=1)
            assert result.barcode == "NEW123"
            assert result.description == "updated"
            mock_session.commit.assert_called_once()
            mock_session.refresh.assert_called_once()
        elif outcome == "conflict":
            with pytest.raises(ConflictError):
                await repo.update_product(dto, product_id=1)
        else:
            with pytest.raises(NotFoundError):
                await repo.update_product(dto, product_id=1)

    @pytest.mark.parametrize(
        "product_exists, outcome",
        [
            (True, "success"),
            (False, "not_found"),
        ],
    )
    async def test_delete_product(self, repo, mock_session, product_exists, outcome):
        product = ProductDAO() if product_exists else None
        mock_session.get = AsyncMock(return_value=product)

        if outcome == "success":
            result = await repo.delete_product(1)
            assert result is True
            mock_session.delete.assert_called_once_with(product)
            mock_session.commit.assert_called_once()
        else:
            with pytest.raises(NotFoundError):
                await repo.delete_product(1)
