from unittest.mock import AsyncMock, MagicMock

import pytest

from app.models.DAO.accounting_dao import AccountingDAO
from app.models.DAO.order_dao import OrderDAO
from app.models.DAO.product_dao import ProductDAO
from app.models.errors.app_error import AppError
from app.models.errors.balance_error import BalanceError
from app.models.errors.notfound_error import NotFoundError
from app.repositories.orders_repository import OrdersRepository


@pytest.fixture
def mock_session():
    """Async context manager"""
    # Used for async with await self._get_session() as session
    session = AsyncMock()
    session.__aenter__.return_value = session
    return session


@pytest.fixture
def repo(mock_session):
    """Injected Orders repository"""
    return OrdersRepository(session=mock_session)


@pytest.mark.asyncio
class TestOrdersRepository:

    @pytest.mark.parametrize(
        "barcode, quantity, price_per_unit",
        [("1502234567865", 5, 1.5)],
    )
    async def test_create_order(
        self, repo, mock_session, barcode, quantity, price_per_unit
    ):
        mock_products_controller = AsyncMock()
        mock_products_controller.get_product_by_barcode.return_value = MagicMock()
        mock_session.add = MagicMock()

        result_DAO = await repo.create_order(
            product_barcode=barcode,
            quantity=quantity,
            price_per_unit=price_per_unit,
            products_controller=mock_products_controller,
        )

        assert isinstance(result_DAO, OrderDAO)
        assert result_DAO.issue_date is not None
        assert result_DAO.product_barcode == barcode
        assert result_DAO.quantity == quantity
        assert result_DAO.price_per_unit == price_per_unit
        assert result_DAO.status == "ISSUED"

        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once_with(result_DAO)

    @pytest.mark.parametrize(
        "list_orders_db, expected_count",
        [([OrderDAO(id=1), OrderDAO(id=2)], 2), ([], 0)],
    )
    async def test_list_orders(
        self, repo, mock_session, list_orders_db, expected_count
    ):
        mock_result = MagicMock()
        mock_session.execute.return_value = mock_result
        mock_result.scalars.return_value.all.return_value = list_orders_db

        orders = await repo.list_orders()

        assert len(orders) == expected_count
        if expected_count > 0:
            assert isinstance(orders[0], OrderDAO)

    @pytest.mark.parametrize(
        "order_id, order_db",
        [
            (
                1,
                OrderDAO(id=1, product_barcode="1502234567865", status="ISSUED"),
            ),
            (999, None),
        ],
    )
    async def test_get_order(self, repo, mock_session, order_id, order_db):
        mock_session.get.return_value = order_db

        result = await repo.get_order(order_id)

        mock_session.get.assert_called_once_with(OrderDAO, order_id)
        if order_db:
            assert isinstance(result, OrderDAO)
            assert result.id == order_id
        else:
            assert result is None

    @pytest.mark.parametrize(
        "order_db, balance_db, expected_exception, expected_msg, expected_status_code",
        [
            # success
            (
                OrderDAO(id=1, quantity=2, price_per_unit=10.0, status="ISSUED"),
                AccountingDAO(balance=100.0),
                None,
                None,
                201,
            ),
            # order status isn't issued
            (
                OrderDAO(id=1, quantity=2, price_per_unit=10.0, status="PAID"),
                AccountingDAO(balance=100.0),
                AppError,
                "Order was not Issued",
                420,
            ),
            # insufficient balance
            (
                OrderDAO(id=1, quantity=5, price_per_unit=50.0, status="ISSUED"),
                AccountingDAO(balance=100.0),
                BalanceError,
                "Insufficient balance for the operation",
                421,
            ),
            # order not found
            (
                None,
                AccountingDAO(balance=100.0),
                NotFoundError,
                "Order with id 1 not found",
                404,
            ),
            # AccountingDAO not found
            (
                OrderDAO(id=1, quantity=1, price_per_unit=10.0, status="ISSUED"),
                None,
                BalanceError,
                "System balance information not found",
                421,
            ),
        ],
    )
    async def test_pay_order(
        self,
        repo,
        mock_session,
        order_db,
        balance_db,
        expected_exception,
        expected_msg,
        expected_status_code,
    ):
        mock_result = MagicMock()
        mock_session.get.return_value = order_db
        mock_session.execute.return_value = mock_result
        mock_result.scalars.return_value.first.return_value = balance_db

        if expected_exception:
            with pytest.raises(expected_exception) as exception_info:
                await repo.pay_order(order_id=1)

            assert expected_msg in str(exception_info.value)

            if expected_status_code:
                assert exception_info.value.status == expected_status_code

            mock_session.commit.assert_not_called()
        else:
            initial_balance = balance_db.balance
            cost = order_db.quantity * order_db.price_per_unit

            result = await repo.pay_order(order_id=1)

            assert result is True
            assert order_db.status == "PAID"
            assert balance_db.balance == initial_balance - cost
            mock_session.commit.assert_called_once()

    @pytest.mark.parametrize(
        "order_db, product_db, expected_exception, expected_quantity, expected_result",
        [
            # success
            (
                OrderDAO(
                    id=1, product_barcode="1502234567865", quantity=10, status="PAID"
                ),
                ProductDAO(barcode="1502234567865", quantity=5, position="A-1-B"),
                None,
                15,
                True,
            ),
            # product exists but position missing
            (
                OrderDAO(id=1, product_barcode="1502234567865", quantity=10),
                ProductDAO(barcode="1502234567865", quantity=5, position=None),
                AppError,
                None,
                None,
            ),
            # order not found
            (None, None, None, None, False),
        ],
    )
    async def test_record_arrival(
        self,
        repo,
        mock_session,
        order_db,
        product_db,
        expected_exception,
        expected_quantity,
        expected_result,
    ):
        mock_result = MagicMock()
        mock_session.get.return_value = order_db
        mock_session.execute.return_value = mock_result
        mock_result.scalars.return_value.first.return_value = product_db

        if expected_exception:
            with pytest.raises(expected_exception) as exc:
                await repo.record_arrival(1)
            assert "Position must be set" in str(exc.value)
        else:
            result = await repo.record_arrival(1)
            assert result == expected_result
            if order_db:
                assert product_db.quantity == expected_quantity
                assert order_db.status == "COMPLETED"
                mock_session.commit.assert_called_once()

    @pytest.mark.parametrize(
        "product_exists, db_balance, expected_exception",
        [
            (True, 100.0, None),  # success
            (False, 100.0, NotFoundError),  # product not found
            (True, 5.0, BalanceError),  # insufficient funds
            (True, None, BalanceError),
        ],
    )
    async def test_create_and_pay_order(
        self, repo, mock_session, product_exists, db_balance, expected_exception
    ):
        input_order = OrderDAO(
            product_barcode="1502234567865", quantity=2, price_per_unit=10.0
        )
        mock_product = ProductDAO(barcode="1502234567865") if product_exists else None
        mock_accounting = (
            AccountingDAO(balance=db_balance) if db_balance is not None else None
        )

        result_product = MagicMock()
        result_product.scalars.return_value.first.return_value = mock_product

        result_accounting = MagicMock()
        result_accounting.scalars.return_value.first.return_value = mock_accounting

        mock_session.execute.side_effect = [result_product, result_accounting]
        mock_session.add = MagicMock()

        if expected_exception:
            with pytest.raises(expected_exception):
                await repo.create_and_pay_order(input_order)

            if db_balance is None and product_exists:
                mock_session.add.assert_called()
                added_obj = mock_session.add.call_args[0][0]
                assert isinstance(added_obj, AccountingDAO)
                assert added_obj.balance == 0.0
        else:
            result = await repo.create_and_pay_order(input_order)
            assert result.status == "PAID"
            assert mock_accounting.balance == db_balance - 20.0
            mock_session.commit.assert_called_once()

    @pytest.mark.parametrize(
        "db_return, expected_exception",
        [
            (OrderDAO(product_barcode="1502234567865"), None),
            (None, NotFoundError),
        ],
    )
    async def test_get_orders_by_barcode(
        self, repo, mock_session, db_return, expected_exception
    ):
        mock_result = MagicMock()
        mock_session.execute.return_value = mock_result
        mock_result.scalars.return_value.first.return_value = db_return

        if expected_exception:
            with pytest.raises(expected_exception):
                await repo.get_orders_by_barcode("1502234567865")
        else:
            result = await repo.get_orders_by_barcode("1502234567865")
            assert result.product_barcode == "1502234567865"
            mock_session.execute.assert_called_once()
