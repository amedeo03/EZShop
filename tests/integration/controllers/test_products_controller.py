from unittest.mock import AsyncMock, MagicMock

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.controllers.products_controller import ProductsController
from app.database.database import Base
from app.models.DTO.product_dto import ProductCreateDTO, ProductUpdateDTO
from app.models.errors.bad_request import BadRequestError
from app.models.errors.conflict_error import ConflictError
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
                    position="1-A-1",
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
                    position="1-A-1",
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
                    position="1-A-1",
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
            (1, None),
            (1, NotFoundError),
            (-1, BadRequestError),
        ],
    )
    async def test_get_product(self, db_session, product_id, expected_exception):
        repo = ProductsRepository(session=db_session)
        controller = ProductsController()
        controller.repo = repo

        dto = ProductCreateDTO(
            description="Milk",
            barcode="4006381333931",
            price_per_unit=1.5,
            note="",
            quantity=10,
            position="1-A-1",
        )

        if expected_exception is None:
            await controller.create_product(dto)
            product = await controller.get_product(product_id)
            assert product.id == product_id
            assert product.description == dto.description
            assert product.barcode == dto.barcode
            assert product.price_per_unit == dto.price_per_unit
            assert product.note == dto.note
            assert product.quantity == dto.quantity
            assert product.position == dto.position

        elif expected_exception is not None:
            with pytest.raises(expected_exception):
                await controller.get_product(product_id)

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "barcode,expected_exception",
        [
            ("4006381333931", None),
            ("9780201379624", NotFoundError),
            ("400638", BadRequestError),
        ],
    )
    async def test_get_product_by_barcode(
        self, db_session, barcode, expected_exception
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
            position="1-A-1",
        )
        await controller.create_product(dto)

        if expected_exception is None:
            product = await controller.get_product_by_barcode(barcode)
            assert product.description == dto.description
            assert product.barcode == dto.barcode
            assert product.price_per_unit == dto.price_per_unit
            assert product.note == dto.note
            assert product.quantity == dto.quantity
            assert product.position == dto.position
        else:
            with pytest.raises(expected_exception):
                await controller.get_product_by_barcode(barcode)

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "description,expected_exception",
        [
            ("Milk", None),
            ("", None),
        ],
    )
    async def test_get_product_by_description(
        self, db_session, description, expected_exception
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
            position="1-A-1",
        )
        await controller.create_product(dto)

        if expected_exception is None:
            product_list = await controller.get_product_by_description(description)
            product = product_list[0]
            assert product.description == dto.description
            assert product.barcode == dto.barcode
            assert product.price_per_unit == dto.price_per_unit
            assert product.note == dto.note
            assert product.quantity == dto.quantity
            assert product.position == dto.position
        else:
            with pytest.raises(expected_exception):
                await controller.get_product_by_description(description)

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "product_id,position,expected_exception",
        [
            (1, "1-B-1", None),
            (12345, "1-B-1", NotFoundError),  # nonexistent product
            (-1, "1-B-1", BadRequestError),  # invalid id
            (1, "B-1", BadRequestError),  # invalid position format
            (1, "1-C-1", ConflictError),  # conflicting position
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
            position="1-A-1",
        )
        dto2 = ProductCreateDTO(  # conflictint product
            description="Coffee",
            barcode="9780201379624",
            price_per_unit=1.5,
            note="",
            quantity=10,
            position="1-C-1",
        )

        await controller.create_product(dto)
        await controller.create_product(dto2)

        if expected_exception is None:
            result = await controller.update_product_position(product_id, position)
            assert result.success == True
            product = await controller.get_product(product_id)
            assert product.position == position
        else:
            with pytest.raises(expected_exception):
                await controller.update_product_position(product_id, position)

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
            position="1-A-1",
        )
        await controller.create_product(dto)

        if expected_exception:
            with pytest.raises(expected_exception):
                await controller.update_product_quantity(product_id, quantity)
        else:
            result = await controller.update_product_quantity(product_id, quantity)
            assert result.success is True

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "product_id, product_update_dto, expected_exception",
        [
            (
                1,
                ProductUpdateDTO(  # correct update
                    description="Milk",
                    barcode="4006381333931",
                    price_per_unit=1.5,
                    note="",
                    quantity=10,
                    position="1-A-1",
                ),
                None,
            ),
            (
                12345,
                ProductUpdateDTO(  # id not found
                    description="Milk",
                    barcode="4006381333931",
                    price_per_unit=1.5,
                    note="",
                    quantity=10,
                    position="1-A-1",
                ),
                NotFoundError,
            ),
            (
                -1,
                ProductUpdateDTO(  # negative id
                    description="Milk",
                    barcode="4006381333931",
                    price_per_unit=1.5,
                    note="",
                    quantity=10,
                    position="1-A-1",
                ),
                BadRequestError,
            ),
            (
                1,
                ProductUpdateDTO(  # invalid barcode
                    description="Milk",
                    barcode="400638",
                    price_per_unit=1.5,
                    note="",
                    quantity=10,
                    position="1-A-1",
                ),
                BadRequestError,
            ),
            (
                1,
                ProductUpdateDTO(  # negative quantity
                    description="Milk",
                    barcode="4006381333931",
                    price_per_unit=1.5,
                    note="",
                    quantity=-10,
                    position="1-A-1",
                ),
                BadRequestError,
            ),
            (
                1,
                ProductUpdateDTO(  # negative price
                    description="Milk",
                    barcode="4006381333931",
                    price_per_unit=-1.5,
                    note="",
                    quantity=10,
                    position="1-A-1",
                ),
                BadRequestError,
            ),
            (
                1,
                ProductUpdateDTO(  # invalid position
                    description="Milk",
                    barcode="4006381333931",
                    price_per_unit=1.5,
                    note="",
                    quantity=10,
                    position="A-1",
                ),
                BadRequestError,
            ),
        ],
    )
    async def test_update_product(
        self, db_session, product_id, product_update_dto, expected_exception
    ):
        repo = ProductsRepository(session=db_session)
        controller = ProductsController()
        controller.repo = repo

        mock_sold_products_controller = AsyncMock()
        mock_orders_controller = AsyncMock()
        mock_returned_products_controller = AsyncMock()

        mock_sold_products_controller.get_sold_product_by_id.side_effect = (
            NotFoundError("NotFound")
        )
        mock_orders_controller.get_order_by_product_barcode.side_effect = NotFoundError(
            "NotFound"
        )
        mock_returned_products_controller.get_returned_products_by_id.side_effect = (
            NotFoundError("NotFound")
        )

        dto = ProductCreateDTO(  # existing product
            description="Coffee",
            barcode="9780201379624",
            price_per_unit=1.5,
            note="",
            quantity=10,
            position="1-B-1",
        )

        await controller.create_product(dto)

        if expected_exception is None:
            result = await controller.update_product(
                product_id,
                product_update_dto,
                mock_sold_products_controller,
                mock_orders_controller,
                mock_returned_products_controller,
            )

            assert result.success == True

        else:
            with pytest.raises(expected_exception):
                await controller.update_product(
                    product_id,
                    product_update_dto,
                    mock_sold_products_controller,
                    mock_orders_controller,
                    mock_returned_products_controller,
                )

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "conflict_type",
        [("sales"), ("returns"), ("orders")],
    )
    async def test_update_product_invalid_state(self, db_session, conflict_type):
        repo = ProductsRepository(session=db_session)
        controller = ProductsController()
        controller.repo = repo

        mock_sold_products_controller = AsyncMock()
        mock_orders_controller = AsyncMock()
        mock_returned_products_controller = AsyncMock()

        dto = ProductCreateDTO(  # existing product
            description="Coffee",
            barcode="9780201379624",
            price_per_unit=1.5,
            note="",
            quantity=10,
            position="1-B-1",
        )
        update_dto = ProductUpdateDTO(
            description="Milk",
            barcode="4006381333931",
            price_per_unit=1.5,
            note="",
            quantity=10,
            position="1-A-1",
        )

        await controller.create_product(dto)

        if conflict_type == "sales":
            mock_sold_products_controller.get_sold_product_by_id.return_value = True
            mock_orders_controller.get_order_by_product_barcode.side_effect = (
                NotFoundError("NotFound")
            )
            mock_returned_products_controller.get_returned_products_by_id.side_effect = NotFoundError(
                "NotFound"
            )
            with pytest.raises(InvalidStateError) as info:
                await controller.update_product(
                    1,
                    update_dto,
                    mock_sold_products_controller,
                    mock_orders_controller,
                    mock_returned_products_controller,
                )

            assert "SALE" in str(info.value)
        elif conflict_type == "returns":
            mock_sold_products_controller.get_sold_product_by_id.side_effect = (
                NotFoundError("NotFound")
            )
            mock_orders_controller.get_order_by_product_barcode.side_effect = (
                NotFoundError("NotFound")
            )
            mock_returned_products_controller.get_returned_products_by_id.return_value = (
                True
            )
            with pytest.raises(InvalidStateError) as info:
                await controller.update_product(
                    1,
                    update_dto,
                    mock_sold_products_controller,
                    mock_orders_controller,
                    mock_returned_products_controller,
                )

            assert "RETURN" in str(info.value)

        elif conflict_type == "orders":
            mock_sold_products_controller.get_sold_product_by_id.side_effect = (
                NotFoundError("NotFound")
            )
            mock_orders_controller.get_order_by_product_barcode.return_value = True
            mock_returned_products_controller.get_returned_products_by_id.side_effect = NotFoundError(
                "NotFound"
            )
            with pytest.raises(InvalidStateError) as info:
                await controller.update_product(
                    1,
                    update_dto,
                    mock_sold_products_controller,
                    mock_orders_controller,
                    mock_returned_products_controller,
                )

            assert "ORDER" in str(info.value)

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "product_id, expected_exception",
        [
            (1, None),
            (12345, NotFoundError),  # nonexistent product
            (-1, BadRequestError),  # invalid id
        ],
    )
    async def test_delete_product(self, db_session, product_id, expected_exception):
        repo = ProductsRepository(session=db_session)
        controller = ProductsController()
        controller.repo = repo

        mock_sold_products_controller = AsyncMock()
        mock_orders_controller = AsyncMock()
        mock_returned_products_controller = AsyncMock()

        dto = ProductCreateDTO(  # existing product
            description="Coffee",
            barcode="9780201379624",
            price_per_unit=1.5,
            note="",
            quantity=10,
            position="1-B-1",
        )

        await controller.create_product(dto)

        mock_sold_products_controller.get_sold_product_by_id.side_effect = (
            NotFoundError("NotFound")
        )
        mock_orders_controller.get_order_by_product_barcode.side_effect = NotFoundError(
            "NotFound"
        )
        mock_returned_products_controller.get_returned_products_by_id.side_effect = (
            NotFoundError("NotFound")
        )

        if expected_exception is None:
            await controller.delete_product(
                product_id,
                mock_sold_products_controller,
                mock_orders_controller,
                mock_returned_products_controller,
            )

            with pytest.raises(NotFoundError):
                await controller.get_product(product_id)
        else:
            with pytest.raises(expected_exception):
                await controller.delete_product(
                    product_id,
                    mock_sold_products_controller,
                    mock_orders_controller,
                    mock_returned_products_controller,
                )

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "conflict_type",
        [("sales"), ("returns"), ("orders")],
    )
    async def test_delete_product_invalid_state(self, db_session, conflict_type):
        repo = ProductsRepository(session=db_session)
        controller = ProductsController()
        controller.repo = repo

        mock_sold_products_controller = AsyncMock()
        mock_orders_controller = AsyncMock()
        mock_returned_products_controller = AsyncMock()

        dto = ProductCreateDTO(  # existing product
            description="Coffee",
            barcode="9780201379624",
            price_per_unit=1.5,
            note="",
            quantity=10,
            position="1-B-1",
        )

        await controller.create_product(dto)

        if conflict_type == "sales":
            mock_sold_products_controller.get_sold_product_by_id.return_value = True
            mock_orders_controller.get_order_by_product_barcode.side_effect = (
                NotFoundError("NotFound")
            )
            mock_returned_products_controller.get_returned_products_by_id.side_effect = NotFoundError(
                "NotFound"
            )
            with pytest.raises(InvalidStateError) as info:
                await controller.delete_product(
                    1,
                    mock_sold_products_controller,
                    mock_orders_controller,
                    mock_returned_products_controller,
                )

            assert "SALE" in str(info.value)
        elif conflict_type == "returns":
            mock_sold_products_controller.get_sold_product_by_id.side_effect = (
                NotFoundError("NotFound")
            )
            mock_orders_controller.get_order_by_product_barcode.side_effect = (
                NotFoundError("NotFound")
            )
            mock_returned_products_controller.get_returned_products_by_id.return_value = (
                True
            )
            with pytest.raises(InvalidStateError) as info:
                await controller.delete_product(
                    1,
                    mock_sold_products_controller,
                    mock_orders_controller,
                    mock_returned_products_controller,
                )

            assert "RETURN" in str(info.value)

        elif conflict_type == "orders":
            mock_sold_products_controller.get_sold_product_by_id.side_effect = (
                NotFoundError("NotFound")
            )
            mock_orders_controller.get_order_by_product_barcode.return_value = True
            mock_returned_products_controller.get_returned_products_by_id.side_effect = NotFoundError(
                "NotFound"
            )
            with pytest.raises(InvalidStateError) as info:
                await controller.delete_product(
                    1,
                    mock_sold_products_controller,
                    mock_orders_controller,
                    mock_returned_products_controller,
                )

            assert "ORDER" in str(info.value)
