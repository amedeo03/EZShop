import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.controllers.products_controller import ProductsController
from app.database.database import Base
from app.models.DTO.product_dto import ProductCreateDTO, ProductUpdateDTO
from app.models.errors.bad_request import BadRequestError
from app.models.errors.invalid_state_error import InvalidStateError
from app.models.errors.notfound_error import NotFoundError
from app.repositories.products_repository import ProductsRepository

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
class TestProductsController:
    @pytest.mark.parametrize(
        "dto,expected_exception",
        [
            (
                ProductCreateDTO(
                    description="Milk",
                    barcode="4006381333931",
                    price_per_unit=1.5,
                    note="",
                    quantity=10,
                    position="A-1-1",
                ),
                None,
            ),
            (
                ProductCreateDTO(
                    description="",
                    barcode="4006381333931",
                    price_per_unit=1.5,
                    note="",
                    quantity=10,
                    position="A-1-1",
                ),
                BadRequestError,
            ),
            (
                ProductCreateDTO(
                    description="Milk",
                    barcode="4006",
                    price_per_unit=1.5,
                    note="",
                    quantity=10,
                    position="A-1-1",
                ),
                BadRequestError,
            ),
        ],
    )
    async def test_create_product(self, db_session, dto, expected_exception):
        repo = ProductsRepository(session=db_session)
        controller = ProductsController()
        controller.repo = repo

        if expected_exception:
            with pytest.raises(expected_exception):
                await controller.create_product(dto)
        else:
            product = await controller.create_product(dto)
            assert product.id is not None
            assert product.description == dto.description
            assert product.barcode == dto.barcode
            assert product.price_per_unit == dto.price_per_unit
            assert product.note == dto.note
            assert product.quantity == dto.quantity
            assert product.position == dto.position

    @pytest.mark.asyncio
    async def test_list_products(self, db_session):
        repo = ProductsRepository(session=db_session)
        controller = ProductsController()
        controller.repo = repo

        products = await controller.list_products()
        assert isinstance(products, list)

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "product_id,expected_exception",
        [
            (1, NotFoundError),
            (-1, BadRequestError),
        ],
    )
    async def test_get_product(self, db_session, product_id, expected_exception):
        repo = ProductsRepository(session=db_session)
        controller = ProductsController()
        controller.repo = repo

        with pytest.raises(expected_exception):
            await controller.get_product(product_id)

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "barcode,expected_exception",
        [
            ("123456789012", Exception),
            ("invalid", BadRequestError),
        ],
    )
    async def test_get_product_by_barcode(
        self, db_session, barcode, expected_exception
    ):
        repo = ProductsRepository(session=db_session)
        controller = ProductsController()
        controller.repo = repo

        with pytest.raises(expected_exception):
            await controller.get_product_by_barcode(barcode)

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "description,expected_exception",
        [
            ("Milk", NotFoundError),
            ("", NotFoundError),
        ],
    )
    async def test_get_product_by_description(
        self, db_session, description, expected_exception
    ):
        repo = ProductsRepository(session=db_session)
        controller = ProductsController()
        controller.repo = repo

        with pytest.raises(expected_exception):
            await controller.get_product_by_description(description)

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "product_id,position,expected_exception",
        [
            (1, "B-1-1", None),
            (12345, "A-1-1", NotFoundError),  # nonexistent product
            (-1, "A-1-1", BadRequestError),  # invalid id
            (1, "A-1", BadRequestError),  # invalid position format
        ],
    )
    async def test_update_product_position(
        self, db_session, product_id, position, expected_exception
    ):
        repo = ProductsRepository(session=db_session)
        controller = ProductsController()
        controller.repo = repo

        dto = ProductCreateDTO(
            description="Milk",
            barcode="4006381333931",
            price_per_unit=1.5,
            note="",
            quantity=10,
            position="A-1-1",
        )
        await controller.create_product(dto)

        if expected_exception:
            with pytest.raises(expected_exception):
                await controller.update_product_position(product_id, position)
        else:
            result = await controller.update_product_position(product_id, position)
            assert result.success is True

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "product_id,quantity,expected_exception",
        [
            (1, 10, None),
            (1, -5, None),
            (12345, 10, NotFoundError),  # nonexistent product
            (-1, 10, BadRequestError),  # invalid id
            (1, -100, BadRequestError),  # invalid position format
        ],
    )
    async def test_update_product_quantity(
        self, db_session, product_id, quantity, expected_exception
    ):
        repo = ProductsRepository(session=db_session)
        controller = ProductsController()
        controller.repo = repo

        dto = ProductCreateDTO(
            description="Milk",
            barcode="4006381333931",
            price_per_unit=1.5,
            note="",
            quantity=10,
            position="A-1-1",
        )
        await controller.create_product(dto)

        if expected_exception:
            with pytest.raises(expected_exception):
                await controller.update_product_quantity(product_id, quantity)
        else:
            result = await controller.update_product_quantity(product_id, quantity)
            assert result.success is True
