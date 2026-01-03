import asyncio

import pytest

from app.models.errors.bad_request import BadRequestError
from app.models.errors.conflict_error import ConflictError
from app.models.errors.notfound_error import NotFoundError
from app.repositories.products_repository import ProductDAO, ProductsRepository
from init_db import init_db, reset


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session", autouse=True)
def reset_db(event_loop):
    event_loop.run_until_complete(reset())
    event_loop.run_until_complete(init_db())


# Tests
class TestProductsRepository:
    expected_products: list[ProductDAO] = []
    created_products: list[ProductDAO] = []

    @pytest.fixture(scope="session")
    def repo(self):
        return ProductsRepository()

    @pytest.fixture(scope="session", autouse=True)
    async def populate_product_repository(self, repo):
        self.expected_products.append(
            ProductDAO(
                description="coffe",
                barcode="4006381333931",
                price_per_unit=1.5,
                quantity=150,
                position="A-1-1",
                note="",
            )
        )
        self.expected_products.append(
            ProductDAO(
                description="milk",
                barcode="9780201379624",
                price_per_unit=1,
                quantity=100,
                position="A-1-2",
                note="",
            )
        )
        self.expected_products.append(
            ProductDAO(
                description="beer",
                barcode="5901234123457",
                price_per_unit=2,
                quantity=80,
                position="A-1-3",
                note="",
            )
        )

        for product in self.expected_products:
            self.created_products.append(
                await repo.create_product(
                    product.description,
                    product.barcode,
                    product.price_per_unit,
                    product.note,
                    product.quantity,
                    product.position,
                )
            )
        return

    @pytest.mark.asyncio
    async def test_list_products(self, repo):
        product_count: int = len(await repo.list_products())
        assert product_count == len(self.expected_products)

    @pytest.mark.asyncio
    async def test_create_new_product(self, repo):
        product: ProductDAO = ProductDAO(
            description="apple",
            barcode="7501031311309",
            price_per_unit=1,
            quantity=135,
            position="A-1-4",
            note="",
        )
        created_product: ProductDAO = await repo.create_product(
            product.description,
            product.barcode,
            product.price_per_unit,
            product.note,
            product.quantity,
            product.position,
        )
        assert created_product.barcode == product.barcode  # type: ignore
        assert created_product.price_per_unit == product.price_per_unit  # type: ignore
        assert created_product.quantity == product.quantity  # type: ignore
        assert created_product.description == product.description  # type: ignore

    @pytest.mark.asyncio
    async def test_create_duplicate_products(self, repo):
        product_barcode_duplicate: ProductDAO = ProductDAO(
            description="coffe",
            barcode="4006381333931",
            price_per_unit=1.5,
            quantity=150,
            position="A-1-0",
            note="",
        )
        product_position_duplicate: ProductDAO = ProductDAO(
            description="beer",
            barcode="8806085724013",
            price_per_unit=1,
            quantity=135,
            position="A-1-1",
            note="",
        )
        with pytest.raises(ConflictError):
            await repo.create_product(
                product_barcode_duplicate.description,
                product_barcode_duplicate.barcode,
                product_barcode_duplicate.price_per_unit,
                product_barcode_duplicate.note,
                product_barcode_duplicate.quantity,
                product_barcode_duplicate.position,
            )

        with pytest.raises(ConflictError):
            await repo.create_product(
                product_position_duplicate.description,
                product_position_duplicate.barcode,
                product_position_duplicate.price_per_unit,
                product_position_duplicate.note,
                product_position_duplicate.quantity,
                product_position_duplicate.position,
            )

    @pytest.mark.asyncio
    async def test_get_product_by_id(self, repo):
        expected_product: ProductDAO = self.created_products[0]
        db_product: ProductDAO = await repo.get_product(expected_product.id)

        assert db_product.barcode == expected_product.barcode  # type: ignore
        assert db_product.price_per_unit == expected_product.price_per_unit  # type: ignore
        assert db_product.quantity == expected_product.quantity  # type: ignore
        assert db_product.description == expected_product.description  # type: ignore

    @pytest.mark.asyncio
    async def test_get_product_by_barcode(self, repo):
        expected_product: ProductDAO = self.created_products[0]
        db_product: ProductDAO = await repo.get_product_by_barcode(
            expected_product.barcode
        )

        assert db_product.barcode == expected_product.barcode  # type: ignore
        assert db_product.price_per_unit == expected_product.price_per_unit  # type: ignore
        assert db_product.quantity == expected_product.quantity  # type: ignore
        assert db_product.description == expected_product.description  # type: ignore

    @pytest.mark.asyncio
    async def test_get_product_by_name(self, repo):
        expected_product: ProductDAO = self.created_products[0]
        db_product: ProductDAO = (
            await repo.get_product_by_description(expected_product.description)
        )[0]

        assert db_product.barcode == expected_product.barcode  # type: ignore
        assert db_product.price_per_unit == expected_product.price_per_unit  # type: ignore
        assert db_product.quantity == expected_product.quantity  # type: ignore
        assert db_product.description == expected_product.description  # type: ignore

    @pytest.mark.asyncio
    async def test_update_product_position(self, repo):
        new_position: str = "B-1-1"
        product: ProductDAO = self.created_products[0]
        updated_product: ProductDAO

        await repo.update_product_position(product.id, new_position)
        updated_product = await repo.get_product(product.id)

        assert updated_product.position == new_position  # type: ignore

    @pytest.mark.asyncio
    async def test_update_product_position_nonexistent_product(self, repo):
        new_position: str = "B-1-1"
        nonexistent_id: int = 12345

        with pytest.raises(NotFoundError):
            await repo.update_product_position(nonexistent_id, new_position)

    @pytest.mark.asyncio
    async def test_update_product_position_conflict(self, repo):
        conflicting_position: str = self.created_products[2].position  # type: ignore
        product: ProductDAO = self.created_products[1]

        with pytest.raises(ConflictError):
            await repo.update_product_position(product.id, conflicting_position)

        not_updated_product = await repo.get_product(product.id)

        assert not_updated_product.position == product.position

    @pytest.mark.asyncio
    async def test_update_product_quantity(self, repo):
        new_quantity: int = 150
        product: ProductDAO = self.created_products[0]
        old_quantity: int = product.quantity  # type: ignore
        updated_product: ProductDAO

        await repo.update_product_quantity(product.id, new_quantity)
        updated_product = await repo.get_product(product.id)

        assert updated_product.quantity == old_quantity + new_quantity  # type: ignore

    @pytest.mark.asyncio
    async def test_update_product_quantity_nonexistent_product(self, repo):
        new_quantity: int = 150
        nonexistent_id: int = 12345

        with pytest.raises(NotFoundError):
            await repo.update_product_quantity(nonexistent_id, new_quantity)

    @pytest.mark.asyncio
    async def test_update_product_quantity_invalid_quantity(self, repo):
        invalid_quantity: int = -200000
        product: ProductDAO = self.created_products[0]

        with pytest.raises(BadRequestError):
            await repo.update_product_quantity(product.id, invalid_quantity)
