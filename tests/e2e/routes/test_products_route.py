import asyncio

import pytest
from fastapi.testclient import TestClient

from init_db import init_db, reset
from main import app


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as c:
        yield c


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


class TestProductsRouter:
    @pytest.mark.parametrize(
        "role, product, expected_exception_code",
        [
            (
                "admin",
                {  # correct product
                    "description": "Test product",
                    "barcode": "123456789012",
                    "price_per_unit": 9.99,
                    "note": "",
                    "quantity": 10,
                    "position": "A-1-1",
                },
                201,
            ),
            (
                "admin",
                {  # invalid barcode
                    "description": "Test product",
                    "barcode": "123",
                    "price_per_unit": 9.99,
                    "note": "",
                    "quantity": 10,
                    "position": "A-1-1",
                },
                400,
            ),
            (
                "admin",
                {  # empty description
                    "description": "",
                    "barcode": "123456789012",
                    "price_per_unit": 9.99,
                    "note": "",
                    "quantity": 10,
                    "position": "A-1-1",
                },
                400,
            ),
            (
                "admin",
                {  # wrong position format
                    "description": "test product",
                    "barcode": "123456789012",
                    "note": "",
                    "quantity": 10,
                    "position": "A-1",
                },
                400,
            ),
            (
                "cashier",
                {  # insufficient rights
                    "description": "Test product",
                    "barcode": "123456789012",
                    "price_per_unit": 9.99,
                    "note": "",
                    "quantity": 10,
                    "position": "A-1-1",
                },
                403,
            ),
            (
                None,
                {  # unauthenticated
                    "description": "Test product",
                    "barcode": "123456789012",
                    "price_per_unit": 9.99,
                    "note": "",
                    "quantity": 10,
                    "position": "A-1-1",
                },
                401,
            ),
        ],
    )
    def test_create_product(
        self, client, auth_tokens, role, product, expected_exception_code
    ):

        headers = auth_header(auth_tokens, role) if role else None
        resp = client.post(
            BASE_URL + "/products",
            json=product,
            headers=headers,
        )

        if expected_exception_code == 400:
            assert resp.status_code in (expected_exception_code, 422)
        else:
            assert resp.status_code == expected_exception_code

    @pytest.mark.parametrize(
        "role, expected_exception_code",
        [
            ("admin", 200),  # success
            ("cashier", 200),  # success
            ("shop_manager", 200),  # success
            (None, 401),  # unauthenticated
        ],
    )
    def test_list_products(self, client, auth_tokens, role, expected_exception_code):

        headers = auth_header(auth_tokens, role) if role else None
        resp = client.get(
            BASE_URL + "/products",
            headers=headers,
        )

        assert resp.status_code == expected_exception_code

    @pytest.mark.parametrize(
        "input_id, role, expected_exception_code",
        [
            (1, "admin", 200),  # success
            (-1, "admin", 400),  # invalid id
            (12345, "admin", 404),  # no product found
            ("abc", "admin", 400),  # invalid id
            (1, None, 401),  # unauthenticated
        ],
    )
    def test_get_product(
        self, client, auth_tokens, input_id, role, expected_exception_code
    ):

        headers = auth_header(auth_tokens, role) if role else None
        product = {
            "description": "Test product",
            "barcode": "123456789012",
            "price_per_unit": 9.99,
            "note": "",
            "quantity": 10,
            "position": "A-1-1",
        }

        client.post(
            BASE_URL + "/products",
            json=product,
            headers=headers,
        )

        resp = client.get(
            BASE_URL + "/products/" + str(input_id),
            headers=headers,
        )

        if expected_exception_code == 400:
            assert resp.status_code in (expected_exception_code, 422)
        else:
            assert resp.status_code == expected_exception_code

    @pytest.mark.parametrize(
        "input_barcode, role, expected_exception_code",
        [
            ("123456789012", "admin", 200),  # success
            ("426", "admin", 400),  # invalid barcode
            ("4260123456788", "admin", 404),  # no product found
            ("", "admin", 400),  # invalid id
            ("123456789012", "cashier", 403),  # insufficient rights
            ("123456789012", None, 401),  # unauthenticated
        ],
    )
    def test_get_product_by_barcode(
        self, client, auth_tokens, input_barcode, role, expected_exception_code
    ):

        headers = auth_header(auth_tokens, role) if role else None
        product = {
            "description": "Test product",
            "barcode": "123456789012",
            "price_per_unit": 9.99,
            "note": "",
            "quantity": 10,
            "position": "A-1-1",
        }

        client.post(
            BASE_URL + "/products",
            json=product,
            headers=headers,
        )

        resp = client.get(
            BASE_URL + "/products/barcode/" + input_barcode,
            headers=headers,
        )

        if expected_exception_code == 400:
            assert resp.status_code in (expected_exception_code, 422)
        else:
            assert resp.status_code == expected_exception_code

    @pytest.mark.parametrize(
        "input_description, role, expected_exception_code",
        [
            ("Test", "admin", 200),  # success
            ("tseT", "admin", 404),  # no product found
            ("Test", "cashier", 403),  # insufficient rights
            ("Test", None, 401),  # unauthenticated
        ],
    )
    def test_get_product_by_description(
        self, client, auth_tokens, input_description, role, expected_exception_code
    ):

        headers = auth_header(auth_tokens, role) if role else None
        product = {
            "description": "Test product",
            "barcode": "123456789012",
            "price_per_unit": 9.99,
            "note": "",
            "quantity": 10,
            "position": "A-1-1",
        }

        client.post(
            BASE_URL + "/products",
            json=product,
            headers=headers,
        )

        resp = client.get(
            BASE_URL + "/products/search?query=" + input_description,
            headers=headers,
        )

        if expected_exception_code == 400:
            assert resp.status_code in (expected_exception_code, 422)
        else:
            assert resp.status_code == expected_exception_code

    @pytest.mark.parametrize(
        "input_id, role, expected_exception_code",
        [
            (1, "admin", 204),  # success
            (-1, "admin", 400),  # invalid id
            (12345, "admin", 404),  # no product found
            ("abc", "admin", 400),  # invalid id
            (1, "cashier", 403),  # insufficient rights
            (1, None, 401),  # unauthenticated
        ],
    )
    def test_delete_product(
        self, client, auth_tokens, input_id, role, expected_exception_code
    ):

        headers = auth_header(auth_tokens, role) if role else None
        product = {
            "description": "Test product",
            "barcode": "123456789012",
            "price_per_unit": 9.99,
            "note": "",
            "quantity": 10,
            "position": "A-1-1",
        }

        client.post(
            BASE_URL + "/products",
            json=product,
            headers=headers,
        )

        resp = client.delete(
            BASE_URL + "/products/" + str(input_id),
            headers=headers,
        )

        if expected_exception_code == 400:
            assert resp.status_code in (expected_exception_code, 422)
        else:
            assert resp.status_code == expected_exception_code

    @pytest.mark.parametrize(
        "product_id, role, product_update, expected_exception_code",
        [
            (
                1,  # correct update
                "admin",
                {
                    "description": "updated product",
                    "barcode": "9780201379624",
                    "price_per_unit": 9.99,
                    "note": "updated note",
                    "quantity": 10,
                    "position": "B-1-1",
                },
                201,
            ),
            (
                -1,  # invalid id
                "admin",
                {
                    "description": "Test product",
                    "barcode": "9780201379624",
                    "price_per_unit": 9.99,
                    "note": "",
                    "quantity": 10,
                    "position": "B-1-1",
                },
                400,
            ),
            (
                1,  # invalid barcode
                "admin",
                {
                    "description": "Test product",
                    "barcode": "12345",
                    "price_per_unit": 9.99,
                    "note": "",
                    "quantity": 10,
                    "position": "B-1-1",
                },
                400,
            ),
            (
                1,  # invalid quantity
                "admin",
                {
                    "description": "Test product",
                    "barcode": "9780201379624",
                    "price_per_unit": 9.99,
                    "note": "",
                    "quantity": -3,
                    "position": "B-1-1",
                },
                400,
            ),
            (
                1,  # invalid price
                "admin",
                {
                    "description": "Test product",
                    "barcode": "9780201379624",
                    "price_per_unit": -9.99,
                    "note": "",
                    "quantity": 10,
                    "position": "B-1-1",
                },
                400,
            ),
            (
                12345,  # not found
                "admin",
                {
                    "description": "Test product",
                    "barcode": "9780201379624",
                    "price_per_unit": 9.99,
                    "note": "",
                    "quantity": 10,
                    "position": "B-1-1",
                },
                404,
            ),
            (
                1,  # insufficient rights
                "cashier",
                {
                    "description": "updated product",
                    "barcode": "9780201379624",
                    "price_per_unit": 9.99,
                    "note": "updated note",
                    "quantity": 10,
                    "position": "B-1-1",
                },
                403,
            ),
            (
                1,  # unauthenticated
                None,
                {
                    "description": "updated product",
                    "barcode": "9780201379624",
                    "price_per_unit": 9.99,
                    "note": "updated note",
                    "quantity": 10,
                    "position": "B-1-1",
                },
                401,
            ),
        ],
    )
    def test_update_product(
        self,
        client,
        auth_tokens,
        product_id,
        role,
        product_update,
        expected_exception_code,
    ):
        headers = auth_header(auth_tokens, role) if role else None
        product = {
            "description": "Test product",
            "barcode": "123456789012",
            "price_per_unit": 9.99,
            "note": "",
            "quantity": 10,
            "position": "A-1-1",
        }

        client.post(  # create product to update
            BASE_URL + "/products",
            json=product,
            headers=headers,
        )

        resp = client.put(
            BASE_URL + "/products/" + str(product_id),
            json=product_update,
            headers=headers,
        )

        if expected_exception_code == 400:
            assert resp.status_code in (expected_exception_code, 422)
        else:
            assert resp.status_code == expected_exception_code

    @pytest.mark.parametrize(
        "product_id, product_update, expected_exception_code",
        [
            (
                1,  # barcode already in use
                {
                    "description": "Test product",
                    "barcode": "4006381333931",
                    "price_per_unit": 9.99,
                    "note": "",
                    "quantity": 10,
                    "position": "A-1-1",
                },
                409,
            ),
            (
                1,  # position already in use
                {
                    "description": "Test product",
                    "barcode": "9780201379624",
                    "price_per_unit": 9.99,
                    "note": "",
                    "quantity": 10,
                    "position": "C-1-1",
                },
                409,
            ),
        ],
    )
    def test_update_product_duplicates(
        self, client, auth_tokens, product_id, product_update, expected_exception_code
    ):
        headers = auth_header(auth_tokens, "admin")
        product = {
            "description": "Test product",
            "barcode": "123456789012",
            "price_per_unit": 9.99,
            "note": "",
            "quantity": 10,
            "position": "B-1-1",
        }

        product2 = {
            "description": "Test product 2",
            "barcode": "4006381333931",
            "price_per_unit": 9.99,
            "note": "",
            "quantity": 10,
            "position": "C-1-1",
        }

        resp = client.post(  # create product to update
            BASE_URL + "/products",
            json=product,
            headers=headers,
        )

        resp = client.post(  # create 2nd product to test conflicts
            BASE_URL + "/products",
            json=product2,
            headers=headers,
        )

        resp = client.put(
            BASE_URL + "/products/" + str(product_id),
            json=product_update,
            headers=headers,
        )

        if expected_exception_code == 400:
            assert resp.status_code in (expected_exception_code, 422)
        else:
            assert resp.status_code == expected_exception_code

    @pytest.mark.parametrize("conflict_type", ["sale", "order"])
    def test_update_product_invalid_state(self, client, auth_tokens, conflict_type):
        headers = auth_header(auth_tokens, "admin")
        product = {
            "description": "Test product",
            "barcode": "9771234567898",
            "price_per_unit": 9.99,
            "note": "",
            "quantity": 10,
            "position": "D-3-1",
        }

        update = {
            "description": "Updated test product",
            "barcode": "9783161484100",
        }

        resp = client.post(  # create product to update
            BASE_URL + "/products",
            json=product,
            headers=headers,
        )

        product_id = 4

        if conflict_type == "sale":
            client.post(  # create new empty sale
                BASE_URL + "/sales",
                headers=headers,
            )
            client.post(  # add created product to the sale
                BASE_URL
                + "/sales/"
                + "1/"
                + "items?"
                + "barcode=9771234567898&"
                + "amount=5",
                headers=headers,
            )

            resp = client.put(  # product cannot be modified if belonging to a sale
                BASE_URL + "/products/" + str(product_id),
                json=update,
                headers=headers,
            )

            assert resp.status_code == 420
        elif conflict_type == "order":
            order = {
                "product_barcode": "9771234567898",
                "quantity": 100,
                "price_per_unit": 9.99,
            }

            client.post(  # new order containing the product
                BASE_URL + "/orders",
                json=order,
                headers=headers,
            )

            resp = client.put(  # product cannot be modified if belonging to an order
                BASE_URL + "/products/" + str(product_id),
                json=update,
                headers=headers,
            )

            assert resp.status_code == 420

    @pytest.mark.parametrize(
        "input_id, role, new_position, expected_exception_code",
        [
            (1, "admin", "Z-1-1", 201),  # success
            (1, "admin", "", 201),  # success
            (-1, "admin", "B-1-1", 400),  # invalid id
            (12345, "admin", "B-1-1", 404),  # no product found
            ("abc", "admin", "B-1-1", 400),  # invalid id
            (1, "admin", "B-1", 400),  # invalid position string
            (1, "admin", "C-1-1", 409),  # position conflict
            (1, "cashier", "Z-1-1", 403),  # insufficient rights
            (1, None, "Z-1-1", 401),  # unauthenticated
        ],
    )
    def test_update_product_position(
        self, client, auth_tokens, input_id, role, new_position, expected_exception_code
    ):
        headers = auth_header(auth_tokens, role) if role else None
        product = {
            "description": "Test product",
            "barcode": "123456789012",
            "price_per_unit": 9.99,
            "note": "",
            "quantity": 10,
            "position": "A-1-1",
        }

        product2 = {
            "description": "Test product 2",
            "barcode": "4006381333931",
            "price_per_unit": 9.99,
            "note": "",
            "quantity": 10,
            "position": "C-1-1",
        }

        client.post(  # create product to update
            BASE_URL + "/products",
            json=product,
            headers=headers,
        )

        client.post(  # create product to test conflicts
            BASE_URL + "/products",
            json=product2,
            headers=headers,
        )

        resp = client.patch(
            BASE_URL
            + "/products/"
            + str(input_id)
            + "/position?position="
            + new_position,
            headers=headers,
        )

        if expected_exception_code == 400:
            assert resp.status_code in (expected_exception_code, 422)
        else:
            assert resp.status_code == expected_exception_code

    @pytest.mark.parametrize(
        "input_id, role, quantity, expected_exception_code",
        [
            (1, "admin", 20, 201),  # success
            (1, "admin", -5, 201),  # success
            (-1, "admin", 20, 400),  # invalid id
            (12345, "admin", 20, 404),  # no product found
            ("abc", "admin", 20, 400),  # invalid id
            (1, "admin", -2000, 400),  # insufficient quaantity available
            (1, "cashier", 20, 403),  # insufficient rights
            (1, None, 20, 401),  # unauthenticated
        ],
    )
    def test_update_product_quantity(
        self, client, auth_tokens, input_id, role, quantity, expected_exception_code
    ):

        headers = auth_header(auth_tokens, role) if role else None
        product = {
            "description": "Test product",
            "barcode": "123456789012",
            "price_per_unit": 9.99,
            "note": "",
            "quantity": 100,
            "position": "A-1-1",
        }

        client.post(  # create product to update
            BASE_URL + "/products",
            json=product,
            headers=headers,
        )

        resp = client.patch(
            BASE_URL
            + "/products/"
            + str(input_id)
            + "/quantity?quantity="
            + str(quantity),
            headers=headers,
        )

        if expected_exception_code == 400:
            assert resp.status_code in (expected_exception_code, 422)
        else:
            assert resp.status_code == expected_exception_code

    @pytest.mark.parametrize("conflict_type", ["sale", "order"])
    def test_delete_product_invalid_state(self, client, auth_tokens, conflict_type):
        headers = auth_header(auth_tokens, "admin")
        product = {
            "description": "Test product",
            "barcode": "9771234567898",
            "price_per_unit": 9.99,
            "note": "",
            "quantity": 10,
            "position": "D-3-1",
        }

        client.post(  # create product to update
            BASE_URL + "/products",
            json=product,
            headers=headers,
        )

        resp = client.get(
            BASE_URL + "/products/barcode/" + "9771234567898",
            headers=headers,
        )

        product_id = resp.json()["id"]

        if conflict_type == "sale":
            client.post(  # create new empty sale
                BASE_URL + "/sales",
                headers=headers,
            )
            client.post(  # add created product to the sale
                BASE_URL
                + "/sales/"
                + "1/"
                + "items?"
                + "barcode=9771234567898&"
                + "amount=5",
                headers=headers,
            )

            resp = client.delete(  # product cannot be modified if belonging to a sale
                BASE_URL + "/products/" + str(product_id),
                headers=headers,
            )

            assert resp.status_code == 420
        elif conflict_type == "order":
            order = {
                "product_barcode": "9771234567898",
                "quantity": 100,
                "price_per_unit": 9.99,
            }

            client.post(  # new order containing the product
                BASE_URL + "/orders",
                json=order,
                headers=headers,
            )

            resp = client.delete(  # product cannot be modified if belonging to an order
                BASE_URL + "/products/" + str(product_id),
                headers=headers,
            )

            assert resp.status_code == 420
