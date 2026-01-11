from datetime import datetime
from unittest.mock import AsyncMock

import pytest
import pytest_asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.controllers.orders_controller import OrdersController
from app.database.database import Base
from app.models.DAO.accounting_dao import AccountingDAO
from app.models.DAO.order_dao import OrderDAO
from app.models.DAO.product_dao import ProductDAO
from app.models.DTO.order_dto import OrderDTO
from app.models.errors.app_error import AppError
from app.models.errors.bad_request import BadRequestError
from app.models.errors.balance_error import BalanceError
from app.models.errors.notfound_error import NotFoundError
from app.repositories.orders_repository import OrdersRepository

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
class TestOrdersController:

    @pytest.mark.parametrize(
        "new_order, product_exists, expected_exception",
        [
            (  # Success
                OrderDTO(
                    product_barcode="1502234567865", price_per_unit=0.3, quantity=5
                ),
                True,
                None,
            ),
            (  # product barocde not found
                OrderDTO(
                    product_barcode="0901234123452", price_per_unit=0.3, quantity=5
                ),
                False,
                NotFoundError,
            ),
            (  # negative quantity
                OrderDTO(
                    product_barcode="1502234567865", price_per_unit=0.3, quantity=-1
                ),
                True,
                BadRequestError,
            ),
        ],
    )
    async def test_create_order(
        self, db_session, new_order, product_exists, expected_exception
    ):
        repo = OrdersRepository(session=db_session)
        controller = OrdersController()
        controller.repo = repo

        mock_products_controller = AsyncMock()
        if not product_exists:
            mock_products_controller.get_product_by_barcode.side_effect = NotFoundError(
                "Not Found"
            )
        else:
            mock_products_controller.get_product_by_barcode.return_value = True

        if expected_exception:
            with pytest.raises(expected_exception):
                await controller.create_order(new_order, mock_products_controller)

            db_result = await db_session.execute(
                select(OrderDAO).where(
                    OrderDAO.product_barcode == new_order.product_barcode
                )
            )
            assert db_result.scalars().first() is None
        else:
            await controller.create_order(new_order, mock_products_controller)

            db_result = await db_session.execute(
                select(OrderDAO).where(
                    OrderDAO.product_barcode == new_order.product_barcode
                )
            )
            saved_order = db_result.scalars().first()
            assert saved_order is not None
            assert saved_order.status == "ISSUED"

    @pytest.mark.asyncio
    async def test_list_orders(self, db_session):
        repo = OrdersRepository(session=db_session)
        controller = OrdersController()
        controller.repo = repo

        order1 = OrderDAO(
            product_barcode="1502234567865",
            quantity=5,
            price_per_unit=1.0,
            status="ISSUED",
        )
        order2 = OrderDAO(
            product_barcode="0901234123452",
            quantity=10,
            price_per_unit=2.0,
            status="PAID",
        )
        db_session.add_all([order1, order2])
        await db_session.commit()

        orders = await controller.list_orders()

        assert len(orders) == 2
        assert isinstance(orders[0], OrderDTO)
        assert orders[0].product_barcode == "1502234567865"

    @pytest.mark.parametrize(
        "initial_balance, order_cost, expected_exception",
        [
            (100.0, 50.0, None),  # success: sufficient balance
            (20.0, 50.0, BalanceError),  # insufficient balance - error
        ],
    )
    @pytest.mark.asyncio
    async def test_pay_order(
        self, db_session, initial_balance, order_cost, expected_exception
    ):
        repo = OrdersRepository(session=db_session)
        controller = OrdersController()
        controller.repo = repo

        accounting = AccountingDAO(balance=initial_balance)
        order = OrderDAO(
            product_barcode="1502234567865",
            quantity=1,
            price_per_unit=order_cost,
            status="ISSUED",
        )
        db_session.add_all([accounting, order])
        await db_session.commit()
        await db_session.refresh(order)

        if expected_exception:
            with pytest.raises(expected_exception):
                await controller.pay_order(order.id)
        else:
            response = await controller.pay_order(order.id)
            assert response.success is True

            db_result = await db_session.execute(
                select(OrderDAO).where(OrderDAO.id == order.id)
            )
            updated_order = db_result.scalars().first()

            assert updated_order.status == "PAID"
            acc_result = await db_session.execute(select(AccountingDAO))
            updated_accounting = acc_result.scalars().first()
            assert updated_accounting.balance == (initial_balance - order_cost)

    @pytest.mark.parametrize(
        "setup_status, search_id_offset, expected_exception, expected_message_error",
        [
            # success, order exists (paid)
            ("PAID", 0, None, None),
            # id not found
            ("PAID", 999, NotFoundError, "not found"),
            # order is not PAID but issued
            ("ISSUED", 0, AppError, "not paid"),
        ],
    )
    @pytest.mark.asyncio
    async def test_record_arrival(
        self,
        db_session,
        setup_status,
        search_id_offset,
        expected_exception,
        expected_message_error,
    ):
        repo = OrdersRepository(session=db_session)
        controller = OrdersController()
        controller.repo = repo

        product = ProductDAO(
            description="tea",
            barcode="1502234567865",
            price_per_unit=1.5,
            quantity=10,
            position="A-1-B",
        )
        order = OrderDAO(
            product_barcode="1502234567865",
            quantity=5,
            price_per_unit=1.5,
            status=setup_status,
            issue_date=datetime.now(),
        )

        db_session.add_all([product, order])
        await db_session.commit()
        await db_session.refresh(order)

        target_id = order.id + search_id_offset

        if expected_exception:
            with pytest.raises(expected_exception) as exception_raised:
                await controller.record_arrival(target_id)
            if expected_message_error:
                assert expected_message_error in str(exception_raised.value)
        else:
            response = await controller.record_arrival(target_id)
            assert response.success is True

            prod_res = await db_session.execute(
                select(ProductDAO).where(ProductDAO.barcode == "1502234567865")
            )
            assert prod_res.scalars().first().quantity == 15

    @pytest.mark.asyncio
    async def test_pay_order_for(self, db_session):
        repo = OrdersRepository(session=db_session)
        controller = OrdersController()
        controller.repo = repo

        product = ProductDAO(
            barcode="1502234567865",
            description="Coffee",
            price_per_unit=2.0,
            quantity=10,
            position="A-1-B",
        )
        accounting = AccountingDAO(balance=100.0)

        db_session.add_all([product, accounting])
        await db_session.commit()

        order_dto = OrderDTO(
            product_barcode="1502234567865", quantity=3, price_per_unit=10.0
        )

        result = await controller.pay_order_for(order_dto)

        order_db = (
            (await db_session.execute(select(OrderDAO).where(OrderDAO.id == result.id)))
            .scalars()
            .first()
        )

        assert order_db is not None
        assert order_db.status == "PAID"
        assert order_db.quantity == 3

        accounting_db = (
            (await db_session.execute(select(AccountingDAO))).scalars().first()
        )
        assert accounting_db.balance == 70.0

    @pytest.mark.parametrize(
        "barcode_to_create, barcode_to_search, expected_exception",
        [
            # success - barcode exists
            ("1502234567865", "1502234567865", None),
            # not found - looking for another barcode
            ("1502234567865", "0901234123452", NotFoundError),
            # invalid barcode
            ("1502234567865", "123456789", BadRequestError),
        ],
    )
    @pytest.mark.asyncio
    async def test_get_order_by_product_barcode(
        self, db_session, barcode_to_create, barcode_to_search, expected_exception
    ):
        repo = OrdersRepository(session=db_session)
        controller = OrdersController()
        controller.repo = repo

        existing_order = OrderDAO(
            product_barcode=barcode_to_create,
            quantity=5,
            price_per_unit=1.5,
            status="ISSUED",
            issue_date=datetime.now(),
        )
        db_session.add(existing_order)
        await db_session.commit()

        if expected_exception:
            with pytest.raises(expected_exception) as exception_raised:
                await controller.get_order_by_product_barcode(barcode_to_search)
            assert exception_raised.value.status in (400, 404)
        else:
            result = await controller.get_order_by_product_barcode(barcode_to_search)

            assert isinstance(result, OrderDTO)
            assert result.product_barcode == barcode_to_search
            assert result.quantity == 5
