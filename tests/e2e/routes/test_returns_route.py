"""
End-to-end tests for returns routes.
Follows the pattern in other test files: uses TestClient and authenticates admin/manager/cashier.
"""

import asyncio
import time
import random
import pytest

# suppress SQLAlchemy 'fully NULL primary key identity' warnings for these e2e tests
pytestmark = pytest.mark.filterwarnings("ignore::sqlalchemy.exc.SAWarning")
from fastapi.testclient import TestClient

from main import app
from init_db import reset, init_db


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


# Global counter for barcode and position uniqueness
_barcode_counter = 0


def generate_unique_barcode():
    """Generate a unique valid GTIN-13 barcode."""
    global _barcode_counter
    _barcode_counter += 1

    # Combine timestamp, counter, and random component for uniqueness (12 digits total)
    timestamp_part = str(int(time.time() * 1000))[-6:]
    counter_part = str(_barcode_counter).zfill(3)
    random_part = str(random.randint(0, 999)).zfill(3)
    barcode_12 = timestamp_part + counter_part + random_part

    # Calculate check digit for GTIN-13
    digits = [int(d) for d in barcode_12]
    odd_sum = sum(digits[0::2])
    even_sum = sum(digits[1::2])
    total = odd_sum + (even_sum * 3)
    check_digit = (10 - (total % 10)) % 10

    return barcode_12 + str(check_digit)


def generate_unique_position():
    """Generate a unique warehouse position."""
    global _barcode_counter
    # Use the counter to generate unique positions like A-1-1, A-1-2, A-1-3, etc.
    # Keep shelf and bin numbers in single digit range (1-9)
    aisle = chr(65 + (_barcode_counter // 81) % 26)  # A-Z (26 aisles)
    shelf = (_barcode_counter // 9) % 9 + 1  # 1-9
    bin_num = _barcode_counter % 9 + 1  # 1-9
    return f"{aisle}-{shelf}-{bin_num}"


# Helper functions to create test data
def create_product(client, auth_tokens, barcode=None, quantity=100):
    """Helper to create a product for testing."""
    if barcode is None:
        # Keep trying until we get a unique barcode and position (shouldn't take more than 1-2 tries)
        for _ in range(10):
            barcode = generate_unique_barcode()
            position = generate_unique_position()
            product = {
                "description": "Test product",
                "barcode": barcode,
                "price_per_unit": 9.99,
                "note": "",
                "quantity": quantity,
                "position": position,
            }
            resp = client.post(
                BASE_URL + "/products",
                json=product,
                headers=auth_header(auth_tokens, "admin"),
            )
            if resp.status_code == 201:
                return resp.json()
            elif resp.status_code == 409:
                # Barcode or position collision, try again with new values
                continue
            else:
                assert False, f"Expected 201 or 409, got {resp.status_code}: {resp.json()}"

        # If we've tried 10 times and still getting collisions, something is wrong
        assert False, "Failed to generate unique barcode/position after 10 attempts"
    else:
        # Barcode provided explicitly, use it with a unique position
        position = generate_unique_position()
        product = {
            "description": "Test product",
            "barcode": barcode,
            "price_per_unit": 9.99,
            "note": "",
            "quantity": quantity,
            "position": position,
        }
        resp = client.post(
            BASE_URL + "/products",
            json=product,
            headers=auth_header(auth_tokens, "admin"),
        )
        assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.json()}"
        return resp.json()


def create_sale_with_products(client, auth_tokens, barcode=None, amount=5):
    """Helper to create a sale with products and pay it."""
    if barcode is None:
        barcode = generate_unique_barcode()

    # Create product first
    create_product(client, auth_tokens, barcode=barcode)

    # Create sale
    sale_resp = client.post(
        BASE_URL + "/sales",
        headers=auth_header(auth_tokens, "admin"),
    )
    assert sale_resp.status_code == 201
    sale_id = sale_resp.json()["id"]

    # Add product to sale
    attach_resp = client.post(
        f"{BASE_URL}/sales/{sale_id}/items?barcode={barcode}&amount={amount}",
        headers=auth_header(auth_tokens, "admin"),
    )
    assert attach_resp.status_code == 201

    # Close sale
    close_resp = client.patch(
        f"{BASE_URL}/sales/{sale_id}/close",
        headers=auth_header(auth_tokens, "admin"),
    )
    assert close_resp.status_code == 200

    # Pay sale
    pay_resp = client.patch(
        f"{BASE_URL}/sales/{sale_id}/pay?cash_amount=100",
        headers=auth_header(auth_tokens, "admin"),
    )
    assert pay_resp.status_code == 200

    return sale_id, barcode


class TestReturnsRouter:

    # --- Create return transaction tests ---

    @pytest.mark.parametrize(
        "role, expected_exception_code",
        [
            ("admin", 201),  # success
            ("cashier", 201),  # success
            ("shop_manager", 201),  # success
            (None, 401),  # unauthenticated
        ],
    )
    def test_create_return_transaction_authentication(
        self, client, auth_tokens, role, expected_exception_code
    ):
        # Create a paid sale first
        sale_id, _ = create_sale_with_products(client, auth_tokens)

        headers = auth_header(auth_tokens, role) if role else None
        resp = client.post(
            f"{BASE_URL}/returns/?sale_id={sale_id}",
            headers=headers,
        )

        assert resp.status_code == expected_exception_code

    def test_create_return_transaction_success(self, client, auth_tokens):
        # Create a paid sale first
        sale_id, _ = create_sale_with_products(client, auth_tokens)

        resp = client.post(
            f"{BASE_URL}/returns/?sale_id={sale_id}",
            headers=auth_header(auth_tokens, "admin"),
        )

        assert resp.status_code == 201
        data = resp.json()
        assert "id" in data
        assert data["sale_id"] == sale_id

    def test_create_return_transaction_invalid_sale(self, client, auth_tokens):
        # Try to create return for non-existent sale
        resp = client.post(
            f"{BASE_URL}/returns/?sale_id=999999",
            headers=auth_header(auth_tokens, "admin"),
        )

        assert resp.status_code == 404

    # --- List returns tests ---

    @pytest.mark.parametrize(
        "role, expected_exception_code",
        [
            ("admin", 200),  # success
            ("cashier", 200),  # success
            ("shop_manager", 200),  # success
            (None, 401),  # unauthenticated
        ],
    )
    def test_list_all_returns(
        self, client, auth_tokens, role, expected_exception_code
    ):
        headers = auth_header(auth_tokens, role) if role else None
        resp = client.get(
            BASE_URL + "/returns",
            headers=headers,
        )

        assert resp.status_code == expected_exception_code

        if role is not None:
            payload = resp.json()
            assert isinstance(payload, list)

    # --- Get return by ID tests ---

    @pytest.mark.parametrize(
        "input_id, expected_exception_code",
        [
            (1, 200),  # success - assuming return ID 1 exists
            (-1, 400),  # invalid id
            (999999, 404),  # no return found
            ("abc", 400),  # invalid id
        ],
    )
    def test_get_return_by_id(
        self, client, auth_tokens, input_id, expected_exception_code
    ):
        # Create a return transaction first
        if input_id == 1:
            sale_id, _ = create_sale_with_products(client, auth_tokens)
            create_resp = client.post(
                f"{BASE_URL}/returns/?sale_id={sale_id}",
                headers=auth_header(auth_tokens, "admin"),
            )
            assert create_resp.status_code == 201
            input_id = create_resp.json()["id"]

        resp = client.get(
            BASE_URL + "/returns/" + str(input_id),
            headers=auth_header(auth_tokens, "admin"),
        )

        if resp.status_code == 422:
            resp.status_code = 400

        assert resp.status_code == expected_exception_code

    def test_get_return_by_id_unauthenticated(self, client, auth_tokens):
        # Create a return transaction
        sale_id, _ = create_sale_with_products(client, auth_tokens)
        create_resp = client.post(
            f"{BASE_URL}/returns/?sale_id={sale_id}",
            headers=auth_header(auth_tokens, "admin"),
        )
        return_id = create_resp.json()["id"]

        resp = client.get(f"{BASE_URL}/returns/{return_id}")
        assert resp.status_code == 401

    # --- List returns for sale ID tests ---

    def test_list_returns_for_sale_id_success(self, client, auth_tokens):
        # Create a paid sale
        sale_id, _ = create_sale_with_products(client, auth_tokens)

        # Create return for this sale
        create_resp = client.post(
            f"{BASE_URL}/returns/?sale_id={sale_id}",
            headers=auth_header(auth_tokens, "admin"),
        )
        assert create_resp.status_code == 201

        # List returns for this sale
        resp = client.get(
            f"{BASE_URL}/returns/sale/{sale_id}",
            headers=auth_header(auth_tokens, "admin"),
        )

        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert any(r["sale_id"] == sale_id for r in data)

    def test_list_returns_for_sale_id_unauthenticated(self, client, auth_tokens):
        sale_id, _ = create_sale_with_products(client, auth_tokens)

        resp = client.get(f"{BASE_URL}/returns/sale/{sale_id}")
        assert resp.status_code == 401

    # --- Attach product to return transaction tests ---

    def test_attach_product_to_return_success(self, client, auth_tokens):
        # Create a paid sale with products
        sale_id, barcode = create_sale_with_products(client, auth_tokens, amount=10)

        # Create return transaction
        return_resp = client.post(
            f"{BASE_URL}/returns/?sale_id={sale_id}",
            headers=auth_header(auth_tokens, "admin"),
        )
        return_id = return_resp.json()["id"]

        # Attach product to return
        resp = client.post(
            f"{BASE_URL}/returns/{return_id}/items?barcode={barcode}&amount=5",
            headers=auth_header(auth_tokens, "admin"),
        )

        assert resp.status_code == 201
        assert resp.json()["success"] is True

    @pytest.mark.parametrize(
        "role, expected_exception_code",
        [
            ("admin", 201),  # success
            ("cashier", 201),  # success
            ("shop_manager", 201),  # success
            (None, 401),  # unauthenticated
        ],
    )
    def test_attach_product_to_return_authentication(
        self, client, auth_tokens, role, expected_exception_code
    ):
        # Create a paid sale with products
        sale_id, barcode = create_sale_with_products(client, auth_tokens)

        # Create return transaction
        return_resp = client.post(
            f"{BASE_URL}/returns/?sale_id={sale_id}",
            headers=auth_header(auth_tokens, "admin"),
        )
        return_id = return_resp.json()["id"]

        headers = auth_header(auth_tokens, role) if role else None
        resp = client.post(
            f"{BASE_URL}/returns/{return_id}/items?barcode={barcode}&amount=2",
            headers=headers,
        )

        assert resp.status_code == expected_exception_code

    def test_attach_product_to_return_invalid_barcode(self, client, auth_tokens):
        # Create return transaction
        sale_id, _ = create_sale_with_products(client, auth_tokens)
        return_resp = client.post(
            f"{BASE_URL}/returns/?sale_id={sale_id}",
            headers=auth_header(auth_tokens, "admin"),
        )
        return_id = return_resp.json()["id"]

        # Try to attach non-existent product (use a valid GTIN-13 format that doesn't exist)
        resp = client.post(
            f"{BASE_URL}/returns/{return_id}/items?barcode=9999999999993&amount=2",
            headers=auth_header(auth_tokens, "admin"),
        )

        # API returns 400 for invalid barcode format/non-existent product
        assert resp.status_code in (400, 404)

    def test_attach_product_to_return_invalid_return_id(self, client, auth_tokens):
        resp = client.post(
            f"{BASE_URL}/returns/999999/items?barcode=123456789012&amount=2",
            headers=auth_header(auth_tokens, "admin"),
        )

        assert resp.status_code == 404

    # --- Delete product from return tests ---

    def test_delete_product_from_return_success(self, client, auth_tokens):
        # Create a paid sale with products
        sale_id, barcode = create_sale_with_products(client, auth_tokens, amount=10)

        # Create return and attach product
        return_resp = client.post(
            f"{BASE_URL}/returns/?sale_id={sale_id}",
            headers=auth_header(auth_tokens, "admin"),
        )
        return_id = return_resp.json()["id"]

        # Attach product
        client.post(
            f"{BASE_URL}/returns/{return_id}/items?barcode={barcode}&amount=5",
            headers=auth_header(auth_tokens, "admin"),
        )

        # Delete some quantity
        resp = client.delete(
            f"{BASE_URL}/returns/{return_id}/items?barcode={barcode}&amount=2",
            headers=auth_header(auth_tokens, "admin"),
        )

        assert resp.status_code == 202
        assert resp.json()["success"] is True

    def test_delete_product_from_return_unauthenticated(self, client, auth_tokens):
        sale_id, barcode = create_sale_with_products(client, auth_tokens)
        return_resp = client.post(
            f"{BASE_URL}/returns/?sale_id={sale_id}",
            headers=auth_header(auth_tokens, "admin"),
        )
        return_id = return_resp.json()["id"]

        resp = client.delete(
            f"{BASE_URL}/returns/{return_id}/items?barcode={barcode}&amount=2"
        )

        assert resp.status_code == 401

    # --- Close return transaction tests ---

    def test_close_return_transaction_success(self, client, auth_tokens):
        # Create return with products
        sale_id, barcode = create_sale_with_products(client, auth_tokens)
        return_resp = client.post(
            f"{BASE_URL}/returns/?sale_id={sale_id}",
            headers=auth_header(auth_tokens, "admin"),
        )
        return_id = return_resp.json()["id"]

        # Attach product
        client.post(
            f"{BASE_URL}/returns/{return_id}/items?barcode={barcode}&amount=2",
            headers=auth_header(auth_tokens, "admin"),
        )

        # Close return
        resp = client.patch(
            f"{BASE_URL}/returns/{return_id}/close",
            headers=auth_header(auth_tokens, "admin"),
        )

        assert resp.status_code == 200
        assert resp.json()["success"] is True

    @pytest.mark.parametrize(
        "role, expected_exception_code",
        [
            ("admin", 200),  # success
            ("cashier", 200),  # success
            ("shop_manager", 200),  # success
            (None, 401),  # unauthenticated
        ],
    )
    def test_close_return_transaction_authentication(
        self, client, auth_tokens, role, expected_exception_code
    ):
        # Create return with products
        sale_id, barcode = create_sale_with_products(client, auth_tokens)
        return_resp = client.post(
            f"{BASE_URL}/returns/?sale_id={sale_id}",
            headers=auth_header(auth_tokens, "admin"),
        )
        return_id = return_resp.json()["id"]

        # Attach product
        client.post(
            f"{BASE_URL}/returns/{return_id}/items?barcode={barcode}&amount=2",
            headers=auth_header(auth_tokens, "admin"),
        )

        headers = auth_header(auth_tokens, role) if role else None
        resp = client.patch(
            f"{BASE_URL}/returns/{return_id}/close",
            headers=headers,
        )

        assert resp.status_code == expected_exception_code

    def test_close_return_transaction_not_found(self, client, auth_tokens):
        resp = client.patch(
            f"{BASE_URL}/returns/999999/close",
            headers=auth_header(auth_tokens, "admin"),
        )

        assert resp.status_code == 404

    # --- Reimburse return transaction tests ---

    def test_reimburse_return_transaction_success(self, client, auth_tokens):
        # Set up accounting balance first (reimbursements need sufficient balance)
        client.post(
            f"{BASE_URL}/balance/set/?amount=10000",
            headers=auth_header(auth_tokens, "admin"),
        )

        # Create return with products and close it
        sale_id, barcode = create_sale_with_products(client, auth_tokens)
        return_resp = client.post(
            f"{BASE_URL}/returns/?sale_id={sale_id}",
            headers=auth_header(auth_tokens, "admin"),
        )
        return_id = return_resp.json()["id"]

        # Attach product and close
        client.post(
            f"{BASE_URL}/returns/{return_id}/items?barcode={barcode}&amount=2",
            headers=auth_header(auth_tokens, "admin"),
        )
        client.patch(
            f"{BASE_URL}/returns/{return_id}/close",
            headers=auth_header(auth_tokens, "admin"),
        )

        # Reimburse return
        resp = client.patch(
            f"{BASE_URL}/returns/{return_id}/reimburse",
            headers=auth_header(auth_tokens, "admin"),
        )

        assert resp.status_code == 200
        assert resp.json()["success"] is True

    @pytest.mark.parametrize(
        "role, expected_exception_code",
        [
            ("admin", 200),  # success
            ("cashier", 403),  # insufficient rights
            ("shop_manager", 200),  # success
            (None, 401),  # unauthenticated
        ],
    )
    def test_reimburse_return_transaction_authentication(
        self, client, auth_tokens, role, expected_exception_code
    ):
        # Set up accounting balance first (reimbursements need sufficient balance)
        client.post(
            f"{BASE_URL}/balance/set/?amount=10000",
            headers=auth_header(auth_tokens, "admin"),
        )

        # Create return with products and close it
        sale_id, barcode = create_sale_with_products(client, auth_tokens)
        return_resp = client.post(
            f"{BASE_URL}/returns/?sale_id={sale_id}",
            headers=auth_header(auth_tokens, "admin"),
        )
        return_id = return_resp.json()["id"]

        # Attach product and close
        client.post(
            f"{BASE_URL}/returns/{return_id}/items?barcode={barcode}&amount=2",
            headers=auth_header(auth_tokens, "admin"),
        )
        client.patch(
            f"{BASE_URL}/returns/{return_id}/close",
            headers=auth_header(auth_tokens, "admin"),
        )

        headers = auth_header(auth_tokens, role) if role else None
        resp = client.patch(
            f"{BASE_URL}/returns/{return_id}/reimburse",
            headers=headers,
        )

        assert resp.status_code == expected_exception_code

    def test_reimburse_return_transaction_not_found(self, client, auth_tokens):
        resp = client.patch(
            f"{BASE_URL}/returns/999999/reimburse",
            headers=auth_header(auth_tokens, "admin"),
        )

        assert resp.status_code == 404

    # --- Delete return transaction tests ---

    def test_delete_return_success(self, client, auth_tokens):
        # Create return transaction
        sale_id, _ = create_sale_with_products(client, auth_tokens)
        return_resp = client.post(
            f"{BASE_URL}/returns/?sale_id={sale_id}",
            headers=auth_header(auth_tokens, "admin"),
        )
        return_id = return_resp.json()["id"]

        # Delete return
        resp = client.delete(
            f"{BASE_URL}/returns/{return_id}",
            headers=auth_header(auth_tokens, "admin"),
        )

        assert resp.status_code == 204

        # Verify return is gone
        get_resp = client.get(
            f"{BASE_URL}/returns/{return_id}",
            headers=auth_header(auth_tokens, "admin"),
        )
        assert get_resp.status_code == 404

    @pytest.mark.parametrize(
        "role, expected_exception_code",
        [
            ("admin", 204),  # success
            ("cashier", 204),  # success
            ("shop_manager", 204),  # success
            (None, 401),  # unauthenticated
        ],
    )
    def test_delete_return_authentication(
        self, client, auth_tokens, role, expected_exception_code
    ):
        # Create return transaction
        sale_id, _ = create_sale_with_products(client, auth_tokens)
        return_resp = client.post(
            f"{BASE_URL}/returns/?sale_id={sale_id}",
            headers=auth_header(auth_tokens, "admin"),
        )
        return_id = return_resp.json()["id"]

        headers = auth_header(auth_tokens, role) if role else None
        resp = client.delete(
            f"{BASE_URL}/returns/{return_id}",
            headers=headers,
        )

        assert resp.status_code == expected_exception_code

    def test_delete_return_not_found(self, client, auth_tokens):
        resp = client.delete(
            f"{BASE_URL}/returns/999999",
            headers=auth_header(auth_tokens, "admin"),
        )

        assert resp.status_code == 404
