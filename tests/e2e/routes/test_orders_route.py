import asyncio
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from app.models.DTO.order_dto import OrderDTO
from init_db import init_db, reset
from main import app

TEST_PRODUCT_ON_DB = {
    "description": "milk",
    "barcode": "1502234567865",
    "price_per_unit": 2.5,
    "quantity": 7,
    "note": "Last milk type",
    "position": "A-1-G",
}


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture(autouse=True)
def setup_db():
    asyncio.run(reset())
    asyncio.run(init_db())
    yield


BASE_URL = "http://127.0.0.1:8000/api/v1"


@pytest.fixture(scope="session", autouse=True)
def auth_tokens(event_loop, client):
    """Authenticate users once and return their JWT tokens."""

    event_loop.run_until_complete(reset())
    event_loop.run_until_complete(init_db())
    users = {
        "admin": {"username": "admin", "password": "admin"},
        "shop_manager": {"username": "ShopManager", "password": "ShManager"},
        "cashier": {"username": "Cashier", "password": "Cashier"},
    }

    tokens = {}
    for role, creds in users.items():
        response = client.post(BASE_URL + "/auth", json=creds)
        assert response.status_code == 200, f"Login failed for {role}"
        tokens[role] = f"Bearer {response.json()['token']}"

    return tokens


def auth_header(tokens, role: str):
    return {"Authorization": tokens[role]}


class TestOrdersRouter:

    @pytest.mark.parametrize(
        "role, expected_status_code",
        [
            ("admin", 404),  # success but product not found
            ("shop_manager", 404),  # success but product not found
            ("cashier", 403),  # unauthorized - insuff. rights
            (None, 401),  # unauthenticated
        ],
    )
    def test_issue_order_authentication(
        self, client, auth_tokens, role, expected_status_code
    ):
        test_product = {
            "product_barcode": "1502234567865",
            "quantity": 2,
            "price_per_unit": 2.5,
        }
        headers = auth_header(auth_tokens, role) if role else None

        resp = client.post(
            f"{BASE_URL}/orders",
            json=test_product,
            headers=headers,
        )
        assert resp.status_code == expected_status_code

    @pytest.mark.parametrize(
        "product_of_the_order, expected_status_code",
        [
            (  # success
                {
                    "product_barcode": "1502234567865",
                    "price_per_unit": 2.5,
                    "quantity": 7,
                },
                201,
            ),
            (  # product not found
                {
                    "product_barcode": "0901234123452",
                    "price_per_unit": 2.5,
                    "quantity": 7,
                },
                404,
            ),
            (  # invalid barcode (12-14 digits)
                {"product_barcode": "123456789", "price_per_unit": 2.5, "quantity": 7},
                400,
            ),
            (  # invalid barcode (GTIN)
                {
                    "product_barcode": "1502234567866",
                    "price_per_unit": 2.5,
                    "quantity": 7,
                },
                400,
            ),
            (  # invalid price_per_unit
                {
                    "product_barcode": "1502234567865",
                    "price_per_unit": -2.5,
                    "quantity": 7,
                },
                400,
            ),
            (  # invalid quantity
                {
                    "product_barcode": "1502234567865",
                    "price_per_unit": 2.5,
                    "quantity": -7,
                },
                400,
            ),
            (  # product_barcode missing field
                {
                    "price_per_unit": 2.5,
                    "quantity": 7,
                },
                400,
            ),
            (  # missing price_per_unit field
                {
                    "product_barcode": "1502234567865",
                    "quantity": 7,
                },
                400,
            ),
            (  # missing quantity field
                {
                    "product_barcode": "1502234567865",
                    "price_per_unit": 2.5,
                },
                400,
            ),
        ],
    )
    def test_issue_order(
        self, client, auth_tokens, product_of_the_order, expected_status_code
    ):
        headers = auth_header(auth_tokens, "admin")
        # product creation
        client.post(
            f"{BASE_URL}/products",
            headers=headers,
            json=TEST_PRODUCT_ON_DB,
        )
        resp = client.post(
            f"{BASE_URL}/orders",
            json=product_of_the_order,
            headers=headers,
        )
        if expected_status_code == 201:
            created_order = resp.json()
            assert created_order["id"] == 1
            assert (
                created_order["product_barcode"]
                == product_of_the_order["product_barcode"]
            )
            assert created_order["quantity"] == product_of_the_order["quantity"]
            assert created_order["status"] == "ISSUED"
            assert (
                created_order["price_per_unit"]
                == product_of_the_order["price_per_unit"]
            )

        assert resp.status_code in (expected_status_code, 422)

    @pytest.mark.parametrize(
        "role, expected_status_code",
        [
            ("admin", 421),  # success but insufficient balance
            ("shop_manager", 421),  # success but but insufficient balance
            ("cashier", 403),  # unauthorized - insuff. rights
            (None, 401),  # unauthenticated
        ],
    )
    def test_pay_order_for_authentication(
        self, client, auth_tokens, role, expected_status_code
    ):
        test_product = {
            "product_barcode": "1502234567865",
            "quantity": 2,
            "price_per_unit": 2.5,
        }
        headers = auth_header(auth_tokens, role) if role else None
        # product creation
        client.post(f"{BASE_URL}/products", json=TEST_PRODUCT_ON_DB, headers=headers)

        resp = client.post(
            f"{BASE_URL}/orders/payfor",
            json=test_product,
            headers=headers,
        )
        assert resp.status_code == expected_status_code

    @pytest.mark.parametrize(
        "product_of_the_order, expected_status_code, balance",
        [
            (  # success - cost=25
                {
                    "product_barcode": "1502234567865",
                    "price_per_unit": 2.5,
                    "quantity": 10,
                },
                201,
                100,
            ),
            (  # insufficient balance - cost = 25
                {
                    "product_barcode": "1502234567865",
                    "price_per_unit": 2.5,
                    "quantity": 10,
                },
                421,
                10,
            ),
            (  # product not found
                {
                    "product_barcode": "0901234123452",
                    "price_per_unit": 2.5,
                    "quantity": 10,
                },
                404,
                100,
            ),
            (  # invalid barcode (12-14 digits)
                {"product_barcode": "123456789", "price_per_unit": 2.5, "quantity": 7},
                400,
                100,
            ),
            (  # invalid barcode (GTIN)
                {
                    "product_barcode": "1502234567866",
                    "price_per_unit": 2.5,
                    "quantity": 10,
                },
                400,
                100,
            ),
            (  # invalid price_per_unit
                {
                    "product_barcode": "1502234567865",
                    "price_per_unit": -2.5,
                    "quantity": 10,
                },
                400,
                100,
            ),
            (  # invalid quantity
                {
                    "product_barcode": "1502234567865",
                    "price_per_unit": 2.5,
                    "quantity": -7,
                },
                400,
                100,
            ),
            (  # product_barcode missing field
                {
                    "price_per_unit": 2.5,
                    "quantity": 10,
                },
                400,
                100,
            ),
            (  # missing price_per_unit field
                {
                    "product_barcode": "1502234567865",
                    "quantity": 10,
                },
                400,
                100,
            ),
            (  # missing quantity field
                {
                    "product_barcode": "1502234567865",
                    "price_per_unit": 2.5,
                },
                400,
                100,
            ),
        ],
    )
    def test_pay_order_for(
        self,
        client,
        auth_tokens,
        product_of_the_order,
        balance,
        expected_status_code,
    ):
        admin_header = auth_header(auth_tokens, "admin")

        # product creation
        client.post(
            f"{BASE_URL}/products", json=TEST_PRODUCT_ON_DB, headers=admin_header
        )
        # balance set
        client.post(f"{BASE_URL}/balance/set?amount={balance}", headers=admin_header)

        result = client.post(
            f"{BASE_URL}/orders/payfor",
            json=product_of_the_order,
            headers=admin_header,
        )

        if expected_status_code == 201:
            created_order = result.json()
            updated_balance_result = client.get(
                f"{BASE_URL}/balance", headers=admin_header
            )
            new_balance = updated_balance_result.json()["balance"]
            assert new_balance == balance - product_of_the_order["price_per_unit"]* product_of_the_order["quantity"] # fmt: skip
            assert created_order["id"] == 1
            assert created_order["product_barcode"] == product_of_the_order["product_barcode"] # fmt: skip

            assert created_order["quantity"] == product_of_the_order["quantity"]
            assert created_order["status"] == "PAID"
            assert created_order["price_per_unit"] == product_of_the_order["price_per_unit"] # fmt: skip
        else:
            assert result.status_code in (expected_status_code, 422)

    @pytest.mark.parametrize(
        "role, expected_status_code",
        [
            ("admin", 200),  # success
            ("shop_manager", 200),  # success
            ("cashier", 403),  # unauthorized - insuff. rights
            (None, 401),  # unauthenticated
        ],
    )
    def test_list_orders(self, client, auth_tokens, role, expected_status_code):
        headers = auth_header(auth_tokens, role) if role else None
        test_product = {
            "product_barcode": "1502234567865",
            "quantity": 2,
            "price_per_unit": 2.5,
        }
        client.post(f"{BASE_URL}/products", json=TEST_PRODUCT_ON_DB, headers=headers)
        client.post(
            f"{BASE_URL}/orders",
            json=test_product,
            headers=headers,
        )
        result = client.get(
            f"{BASE_URL}/orders",
            headers=headers,
        )
        assert result.status_code == expected_status_code
        if expected_status_code == 200:
            assert len(list(result.json())) == 1

    @pytest.mark.parametrize(
        "role, expected_status_code",
        [
            ("admin", 201),  # success
            ("shop_manager", 201),  # success
            ("cashier", 403),  # unauthorized - insuff. rights
            (None, 401),  # unauthenticated
        ],
    )
    def test_pay_order_authentication(
        self, client, auth_tokens, role, expected_status_code
    ):
        test_product = {
            "product_barcode": "1502234567865",
            "quantity": 10,
            "price_per_unit": 2.5,
        }
        admin_header = auth_header(auth_tokens, "admin")
        headers = auth_header(auth_tokens, role) if role else None
        # product creation
        client.post(
            f"{BASE_URL}/products", json=TEST_PRODUCT_ON_DB, headers=admin_header
        )

        # balance set
        client.post(
            f"{BASE_URL}/balance/set?amount=500",
            headers=admin_header,
        )

        # order creation
        client.post(
            f"{BASE_URL}/orders",
            json=test_product,
            headers=admin_header,
        )

        result = client.patch(
            f"{BASE_URL}/orders/1/pay",
            headers=headers,
        )

        assert result.status_code == expected_status_code

    @pytest.mark.parametrize(
        "order_status_on_db, balance_on_db, order_id, expected_status_code",
        [
            (None, 500, 1, 201),  # success
            (None, 5, 1, 421),  # insufficient balance
            ("PAID", 500, 1, 420),  # invalid status
            (None, 500, 50, 404),  # order not found
            (None, 500, -100, 400),  # invalid id
            (None, 500, "abc", 400),  # invalid id
        ],
    )
    def test_pay_order(
        self,
        client,
        auth_tokens,
        order_status_on_db,
        balance_on_db,
        order_id,
        expected_status_code,
    ):
        test_product = {
            "product_barcode": "1502234567865",
            "quantity": 10,
            "price_per_unit": 2.5,
        }
        admin_header = auth_header(auth_tokens, "admin")
        # product creation
        client.post(
            f"{BASE_URL}/products", json=TEST_PRODUCT_ON_DB, headers=admin_header
        )

        # balance set
        client.post(
            f"{BASE_URL}/balance/set?amount={balance_on_db}",
            headers=admin_header,
        )

        # order creation
        if order_status_on_db == "PAID":
            client.post(
                f"{BASE_URL}/orders/payfor",
                json=test_product,
                headers=admin_header,
            )
        else:
            client.post(
                f"{BASE_URL}/orders",
                json=test_product,
                headers=admin_header,
            )

        result = client.patch(
            f"{BASE_URL}/orders/{order_id}/pay",
            headers=admin_header,
        )

        if expected_status_code == 201:
            result_json = result.json()
            balance_result = client.get(f"{BASE_URL}/balance", headers=admin_header)
            new_balance = balance_result.json()["balance"]

            all_orders_result = client.get(f"{BASE_URL}/orders", headers=admin_header)
            first_order = all_orders_result.json()[0]
            assert first_order["status"] == "PAID"
            assert result_json["success"] == True
            assert new_balance == balance_on_db - (
                test_product["price_per_unit"] * test_product["quantity"]
            )

    @pytest.mark.parametrize(
        "role, expected_status_code",
        [
            ("admin", 201),  # success
            ("shop_manager", 201),  # success
            ("cashier", 403),  # unauthorized - insuff. rights
            (None, 401),  # unauthenticated
        ],
    )
    def test_record_arrival_authentication(
        self, client, auth_tokens, role, expected_status_code
    ):
        test_product = {
            "product_barcode": "1502234567865",
            "quantity": 10,
            "price_per_unit": 2.5,
        }
        admin_header = auth_header(auth_tokens, "admin")
        headers = auth_header(auth_tokens, role) if role else None
        # product creation
        client.post(
            f"{BASE_URL}/products", json=TEST_PRODUCT_ON_DB, headers=admin_header
        )

        # balance set
        client.post(
            f"{BASE_URL}/balance/set?amount=500",
            headers=admin_header,
        )

        # order creation + pay
        client.post(
            f"{BASE_URL}/orders/payfor",
            json=test_product,
            headers=admin_header,
        )

        result = client.patch(
            f"{BASE_URL}/orders/1/arrival",
            headers=headers,
        )

        assert result.status_code == expected_status_code

    @pytest.mark.parametrize(
        "order_status_on_db, balance_on_db, order_id, expected_status_code",
        [
            (None, 500, 1, 201),  # success
            (None, 5, 1, 421),  # insufficient balance
            ("ISSUED", 500, 1, 420),  # invalid status
            (None, 500, 50, 404),  # order not found
            (None, 500, -100, 400),  # invalid id
            (None, 500, "abc", 400),  # invalid id
        ],
    )
    def test_record_arrival(
        self,
        client,
        auth_tokens,
        order_status_on_db,
        balance_on_db,
        order_id,
        expected_status_code,
    ):
        test_product = {
            "product_barcode": "1502234567865",
            "quantity": 10,
            "price_per_unit": 2.5,
        }
        admin_header = auth_header(auth_tokens, "admin")
        # product creation
        client.post(
            f"{BASE_URL}/products", json=TEST_PRODUCT_ON_DB, headers=admin_header
        )

        # balance set
        client.post(
            f"{BASE_URL}/balance/set?amount={balance_on_db}",
            headers=admin_header,
        )

        # order creation
        if order_status_on_db == "ISSUED":
            client.post(
                f"{BASE_URL}/orders/",
                json=test_product,
                headers=admin_header,
            )
        else:
            client.post(
                f"{BASE_URL}/orders/payfor",
                json=test_product,
                headers=admin_header,
            )

        result = client.patch(
            f"{BASE_URL}/orders/{order_id}/arrival",
            headers=admin_header,
        )
        balance_result = client.get(f"{BASE_URL}/balance", headers=admin_header)
        new_balance = balance_result.json()["balance"]

        if expected_status_code == 201:
            result_json = result.json()
            all_orders_result = client.get(f"{BASE_URL}/orders", headers=admin_header)
            first_order = all_orders_result.json()[0]
            product_on_db_result = client.get(f"{BASE_URL}/products", headers=admin_header) # fmt: skip
            product_on_db = product_on_db_result.json()[0]

            assert product_on_db["quantity"] == TEST_PRODUCT_ON_DB["quantity"] + test_product["quantity"] # fmt: skip
            print(
                f"DEBUG: {product_on_db['quantity']=}, {TEST_PRODUCT_ON_DB['quantity']=}, {test_product['quantity']=}"
            )
            assert result_json["success"] == True
            assert new_balance == balance_on_db - (
                test_product["price_per_unit"] * test_product["quantity"]
            )
            assert first_order["status"] == "COMPLETED"
