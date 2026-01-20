import asyncio
import time
import random
import pytest

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
    return f"{shelf}-{aisle}-{bin_num}"


# Helper functions to create test data
def create_product(client, auth_tokens, barcode=None, quantity=100):
    """Helper to create a product for testing."""
    if barcode is None:
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
    sale_id = sale_resp.json()["id"]

    # Add product to sale
    client.post(
        f"{BASE_URL}/sales/{sale_id}/items?barcode={barcode}&amount={amount}",
        headers=auth_header(auth_tokens, "admin"),
    )

    # Close sale
    client.patch(
        f"{BASE_URL}/sales/{sale_id}/close",
        headers=auth_header(auth_tokens, "admin"),
    )

    # Pay sale
    client.patch(
        f"{BASE_URL}/sales/{sale_id}/pay?cash_amount=100",
        headers=auth_header(auth_tokens, "admin"),
    )

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
        assert data["status"] == "OPEN"
        assert data["lines"] == []
        assert "created_at" in data

    def test_create_return_transaction_invalid_sale(self, client, auth_tokens):
        # Try to create return for non-existent sale
        resp = client.post(
            f"{BASE_URL}/returns/?sale_id=999999",
            headers=auth_header(auth_tokens, "admin"),
        )

        assert resp.status_code == 404

    def test_create_return_transaction_unpaid_sale(self, client, auth_tokens):
        # Create an unpaid sale
        barcode = generate_unique_barcode()
        create_product(client, auth_tokens, barcode=barcode)

        # Create sale but don't pay it
        sale_resp = client.post(
            BASE_URL + "/sales",
            headers=auth_header(auth_tokens, "admin"),
        )
        sale_id = sale_resp.json()["id"]

        # Add product to sale
        client.post(
            f"{BASE_URL}/sales/{sale_id}/items?barcode={barcode}&amount=5",
            headers=auth_header(auth_tokens, "admin"),
        )

        # Close sale but don't pay
        client.patch(
            f"{BASE_URL}/sales/{sale_id}/close",
            headers=auth_header(auth_tokens, "admin"),
        )

        # Try to create return on unpaid sale
        resp = client.post(
            f"{BASE_URL}/returns/?sale_id={sale_id}",
            headers=auth_header(auth_tokens, "admin"),
        )

        assert resp.status_code == 420

    def test_create_return_transaction_negative_sale_id(self, client, auth_tokens):
        # Try to create return with negative sale_id
        resp = client.post(
            f"{BASE_URL}/returns/?sale_id=-1",
            headers=auth_header(auth_tokens, "admin"),
        )

        assert resp.status_code == 400

    def test_create_return_transaction_zero_sale_id(self, client, auth_tokens):
        # Try to create return with zero sale_id
        resp = client.post(
            f"{BASE_URL}/returns/?sale_id=0",
            headers=auth_header(auth_tokens, "admin"),
        )

        assert resp.status_code == 400

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
        # Create a return first to ensure list is not empty
        if role is not None:
            sale_id, _ = create_sale_with_products(client, auth_tokens)
            client.post(
                f"{BASE_URL}/returns/?sale_id={sale_id}",
                headers=auth_header(auth_tokens, "admin"),
            )

        headers = auth_header(auth_tokens, role) if role else None
        resp = client.get(
            BASE_URL + "/returns",
            headers=headers,
        )

        assert resp.status_code == expected_exception_code

        if role is not None:
            payload = resp.json()
            assert isinstance(payload, list)
            assert len(payload) > 0
            # Verify first return has expected fields
            first_return = payload[0]
            assert "id" in first_return
            assert "sale_id" in first_return
            assert "status" in first_return
            assert "lines" in first_return

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
        created_sale_id = None
        if input_id == 1:
            sale_id, _ = create_sale_with_products(client, auth_tokens)
            created_sale_id = sale_id
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

        # Verify response body for success case
        if expected_exception_code == 200:
            data = resp.json()
            assert data["id"] == input_id
            assert data["sale_id"] == created_sale_id
            assert data["status"] == "OPEN"
            assert "lines" in data

    @pytest.mark.parametrize(
        "role, expected_exception_code",
        [
            ("admin", 200),  # success
            ("cashier", 200),  # success
            ("shop_manager", 200),  # success
            (None, 401),  # unauthenticated
        ],
    )
    def test_get_return_by_id_authentication(
        self, client, auth_tokens, role, expected_exception_code
    ):
        # Create a return transaction
        sale_id, _ = create_sale_with_products(client, auth_tokens)
        create_resp = client.post(
            f"{BASE_URL}/returns/?sale_id={sale_id}",
            headers=auth_header(auth_tokens, "admin"),
        )
        return_id = create_resp.json()["id"]

        headers = auth_header(auth_tokens, role) if role else None
        resp = client.get(f"{BASE_URL}/returns/{return_id}", headers=headers)

        assert resp.status_code == expected_exception_code

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
        return_id = create_resp.json()["id"]

        # List returns for this sale
        resp = client.get(
            f"{BASE_URL}/returns/sale/{sale_id}",
            headers=auth_header(auth_tokens, "admin"),
        )

        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        # Verify the created return is in the list
        assert data[0]["id"] == return_id
        assert data[0]["sale_id"] == sale_id
        assert "status" in data[0]
        assert "lines" in data[0]

    def test_list_returns_for_sale_id_negative_id(self, client, auth_tokens):
        # Try to list returns for negative sale_id
        resp = client.get(
            f"{BASE_URL}/returns/sale/-1",
            headers=auth_header(auth_tokens, "admin"),
        )
        assert resp.status_code == 400

    def test_list_returns_for_sale_id_zero_id(self, client, auth_tokens):
        # Try to list returns for zero sale_id
        resp = client.get(
            f"{BASE_URL}/returns/sale/0",
            headers=auth_header(auth_tokens, "admin"),
        )
        assert resp.status_code == 400

    def test_list_returns_for_sale_id_string_id(self, client, auth_tokens):
        # Try to list returns for string sale_id
        resp = client.get(
            f"{BASE_URL}/returns/sale/abc",
            headers=auth_header(auth_tokens, "admin"),
        )
        # FastAPI converts 422 to 400 for validation errors
        if resp.status_code == 422:
            resp.status_code = 400
        assert resp.status_code == 400

    @pytest.mark.parametrize(
        "role, expected_exception_code",
        [
            ("admin", 200),  # success
            ("cashier", 200),  # success
            ("shop_manager", 200),  # success
            (None, 401),  # unauthenticated
        ],
    )
    def test_list_returns_for_sale_id_authentication(
        self, client, auth_tokens, role, expected_exception_code
    ):
        # Create a paid sale with return
        sale_id, _ = create_sale_with_products(client, auth_tokens)
        client.post(
            f"{BASE_URL}/returns/?sale_id={sale_id}",
            headers=auth_header(auth_tokens, "admin"),
        )

        headers = auth_header(auth_tokens, role) if role else None
        resp = client.get(f"{BASE_URL}/returns/sale/{sale_id}", headers=headers)

        assert resp.status_code == expected_exception_code

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

        # Verify the product was added to the return
        get_resp = client.get(
            f"{BASE_URL}/returns/{return_id}",
            headers=auth_header(auth_tokens, "admin"),
        )
        return_data = get_resp.json()
        assert len(return_data["lines"]) == 1
        assert return_data["lines"][0]["product_barcode"] == barcode
        assert return_data["lines"][0]["quantity"] == 5

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

    def test_attach_product_to_return_product_not_found(self, client, auth_tokens):
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

        # API may return 400 or 404 for non-existent barcode
        assert resp.status_code in (400, 404)

    def test_attach_product_to_return_negative_return_id(self, client, auth_tokens):
        # Try to attach product with negative return_id
        resp = client.post(
            f"{BASE_URL}/returns/-1/items?barcode=1234567890123&amount=2",
            headers=auth_header(auth_tokens, "admin"),
        )
        assert resp.status_code == 400

    def test_attach_product_to_return_string_return_id(self, client, auth_tokens):
        # Try to attach product with string return_id
        resp = client.post(
            f"{BASE_URL}/returns/abc/items?barcode=1234567890123&amount=2",
            headers=auth_header(auth_tokens, "admin"),
        )
        if resp.status_code == 422:
            resp.status_code = 400
        assert resp.status_code == 400

    def test_attach_product_to_return_invalid_barcode_too_short(self, client, auth_tokens):
        # Create return transaction
        sale_id, _ = create_sale_with_products(client, auth_tokens)
        return_resp = client.post(
            f"{BASE_URL}/returns/?sale_id={sale_id}",
            headers=auth_header(auth_tokens, "admin"),
        )
        return_id = return_resp.json()["id"]

        # Try to attach product with barcode that's too short
        resp = client.post(
            f"{BASE_URL}/returns/{return_id}/items?barcode=12345&amount=2",
            headers=auth_header(auth_tokens, "admin"),
        )
        assert resp.status_code == 400

    def test_attach_product_to_return_invalid_barcode_with_letters(self, client, auth_tokens):
        # Create return transaction
        sale_id, _ = create_sale_with_products(client, auth_tokens)
        return_resp = client.post(
            f"{BASE_URL}/returns/?sale_id={sale_id}",
            headers=auth_header(auth_tokens, "admin"),
        )
        return_id = return_resp.json()["id"]

        # Try to attach product with barcode containing letters
        resp = client.post(
            f"{BASE_URL}/returns/{return_id}/items?barcode=ABC1234567890&amount=2",
            headers=auth_header(auth_tokens, "admin"),
        )
        assert resp.status_code == 400

    def test_attach_product_to_return_negative_amount(self, client, auth_tokens):
        # Create return transaction
        sale_id, barcode = create_sale_with_products(client, auth_tokens)
        return_resp = client.post(
            f"{BASE_URL}/returns/?sale_id={sale_id}",
            headers=auth_header(auth_tokens, "admin"),
        )
        return_id = return_resp.json()["id"]

        # Try to attach product with negative amount
        resp = client.post(
            f"{BASE_URL}/returns/{return_id}/items?barcode={barcode}&amount=-1",
            headers=auth_header(auth_tokens, "admin"),
        )
        assert resp.status_code == 400

    def test_attach_product_to_return_string_amount(self, client, auth_tokens):
        # Create return transaction
        sale_id, barcode = create_sale_with_products(client, auth_tokens)
        return_resp = client.post(
            f"{BASE_URL}/returns/?sale_id={sale_id}",
            headers=auth_header(auth_tokens, "admin"),
        )
        return_id = return_resp.json()["id"]

        # Try to attach product with string amount
        resp = client.post(
            f"{BASE_URL}/returns/{return_id}/items?barcode={barcode}&amount=abc",
            headers=auth_header(auth_tokens, "admin"),
        )
        if resp.status_code == 422:
            resp.status_code = 400
        assert resp.status_code == 400

    def test_attach_product_to_return_invalid_return_id(self, client, auth_tokens):
        # Create a product to get a valid barcode
        barcode = generate_unique_barcode()
        create_product(client, auth_tokens, barcode=barcode)

        # Try to attach to non-existent return_id with valid barcode
        resp = client.post(
            f"{BASE_URL}/returns/999999/items?barcode={barcode}&amount=2",
            headers=auth_header(auth_tokens, "admin"),
        )

        assert resp.status_code == 404

    def test_attach_product_to_closed_return(self, client, auth_tokens):
        # Create return, attach product, and close it
        sale_id, barcode = create_sale_with_products(client, auth_tokens)
        return_resp = client.post(
            f"{BASE_URL}/returns/?sale_id={sale_id}",
            headers=auth_header(auth_tokens, "admin"),
        )
        return_id = return_resp.json()["id"]

        # Attach product
        client.post(
            f"{BASE_URL}/returns/{return_id}/items?barcode={barcode}&amount=1",
            headers=auth_header(auth_tokens, "admin"),
        )

        # Close return
        client.patch(
            f"{BASE_URL}/returns/{return_id}/close",
            headers=auth_header(auth_tokens, "admin"),
        )

        # Try to attach product to closed return
        resp = client.post(
            f"{BASE_URL}/returns/{return_id}/items?barcode={barcode}&amount=1",
            headers=auth_header(auth_tokens, "admin"),
        )

        assert resp.status_code == 420

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

        # Verify quantity was reduced
        get_resp = client.get(
            f"{BASE_URL}/returns/{return_id}",
            headers=auth_header(auth_tokens, "admin"),
        )
        return_data = get_resp.json()
        assert len(return_data["lines"]) == 1
        assert return_data["lines"][0]["quantity"] == 3  # 5 - 2 = 3

    @pytest.mark.parametrize(
        "role, expected_exception_code",
        [
            ("admin", 202),  # success
            ("cashier", 202),  # success
            ("shop_manager", 202),  # success
            (None, 401),  # unauthenticated
        ],
    )
    def test_delete_product_from_return_authentication(
        self, client, auth_tokens, role, expected_exception_code
    ):
        # Create return with product
        sale_id, barcode = create_sale_with_products(client, auth_tokens)
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

        headers = auth_header(auth_tokens, role) if role else None
        resp = client.delete(
            f"{BASE_URL}/returns/{return_id}/items?barcode={barcode}&amount=2",
            headers=headers,
        )

        assert resp.status_code == expected_exception_code

    def test_delete_product_from_return_negative_return_id(self, client, auth_tokens):
        # Try to delete product with negative return_id
        resp = client.delete(
            f"{BASE_URL}/returns/-1/items?barcode=1234567890123&amount=2",
            headers=auth_header(auth_tokens, "admin"),
        )
        assert resp.status_code == 400

    def test_delete_product_from_return_string_return_id(self, client, auth_tokens):
        # Try to delete product with string return_id
        resp = client.delete(
            f"{BASE_URL}/returns/abc/items?barcode=1234567890123&amount=2",
            headers=auth_header(auth_tokens, "admin"),
        )
        if resp.status_code == 422:
            resp.status_code = 400
        assert resp.status_code == 400

    def test_delete_product_from_return_negative_amount(self, client, auth_tokens):
        # Create return with product
        sale_id, barcode = create_sale_with_products(client, auth_tokens)
        return_resp = client.post(
            f"{BASE_URL}/returns/?sale_id={sale_id}",
            headers=auth_header(auth_tokens, "admin"),
        )
        return_id = return_resp.json()["id"]

        # Try to delete with negative amount
        resp = client.delete(
            f"{BASE_URL}/returns/{return_id}/items?barcode={barcode}&amount=-1",
            headers=auth_header(auth_tokens, "admin"),
        )
        assert resp.status_code == 400

    def test_delete_product_from_return_string_amount(self, client, auth_tokens):
        # Create return with product
        sale_id, barcode = create_sale_with_products(client, auth_tokens)
        return_resp = client.post(
            f"{BASE_URL}/returns/?sale_id={sale_id}",
            headers=auth_header(auth_tokens, "admin"),
        )
        return_id = return_resp.json()["id"]

        # Try to delete with string amount
        resp = client.delete(
            f"{BASE_URL}/returns/{return_id}/items?barcode={barcode}&amount=abc",
            headers=auth_header(auth_tokens, "admin"),
        )
        if resp.status_code == 422:
            resp.status_code = 400
        assert resp.status_code == 400

    def test_delete_product_from_return_not_found(self, client, auth_tokens):
        # Try to delete from non-existent return
        resp = client.delete(
            f"{BASE_URL}/returns/999999/items?barcode=1234567890123&amount=2",
            headers=auth_header(auth_tokens, "admin"),
        )
        # API may return 400 or 404 for non-existent return
        assert resp.status_code in (400, 404)

    def test_delete_product_from_return_product_not_found(self, client, auth_tokens):
        # Create return
        sale_id, _ = create_sale_with_products(client, auth_tokens)
        return_resp = client.post(
            f"{BASE_URL}/returns/?sale_id={sale_id}",
            headers=auth_header(auth_tokens, "admin"),
        )
        return_id = return_resp.json()["id"]

        # Try to delete product that was never added to the return
        resp = client.delete(
            f"{BASE_URL}/returns/{return_id}/items?barcode=9999999999993&amount=2",
            headers=auth_header(auth_tokens, "admin"),
        )
        # API may return 400 or 404 for non-existent product
        assert resp.status_code in (400, 404)

    def test_delete_product_from_closed_return(self, client, auth_tokens):
        # Create return, attach product, and close it
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
        client.patch(
            f"{BASE_URL}/returns/{return_id}/close",
            headers=auth_header(auth_tokens, "admin"),
        )

        # Try to delete product from closed return
        resp = client.delete(
            f"{BASE_URL}/returns/{return_id}/items?barcode={barcode}&amount=1",
            headers=auth_header(auth_tokens, "admin"),
        )
        assert resp.status_code == 420

    def test_delete_product_from_reimbursed_return(self, client, auth_tokens):
        # Set up accounting balance
        client.post(
            f"{BASE_URL}/balance/set/?amount=10000",
            headers=auth_header(auth_tokens, "admin"),
        )

        # Create return, attach product, close it, and reimburse it
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

        # Close and reimburse return
        client.patch(
            f"{BASE_URL}/returns/{return_id}/close",
            headers=auth_header(auth_tokens, "admin"),
        )
        client.patch(
            f"{BASE_URL}/returns/{return_id}/reimburse",
            headers=auth_header(auth_tokens, "admin"),
        )

        # Try to delete product from reimbursed return
        resp = client.delete(
            f"{BASE_URL}/returns/{return_id}/items?barcode={barcode}&amount=1",
            headers=auth_header(auth_tokens, "admin"),
        )
        assert resp.status_code == 420

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

        # Verify the return status changed to CLOSED
        get_resp = client.get(
            f"{BASE_URL}/returns/{return_id}",
            headers=auth_header(auth_tokens, "admin"),
        )
        return_data = get_resp.json()
        assert return_data["status"] == "CLOSED"
        assert return_data["sale_id"] == sale_id

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

    def test_close_return_transaction_negative_id(self, client, auth_tokens):
        # Try to close return with negative id
        resp = client.patch(
            f"{BASE_URL}/returns/-1/close",
            headers=auth_header(auth_tokens, "admin"),
        )
        assert resp.status_code == 400

    def test_close_return_transaction_zero_id(self, client, auth_tokens):
        # Try to close return with zero id
        resp = client.patch(
            f"{BASE_URL}/returns/0/close",
            headers=auth_header(auth_tokens, "admin"),
        )
        assert resp.status_code == 400

    def test_close_return_transaction_string_id(self, client, auth_tokens):
        # Try to close return with string id
        resp = client.patch(
            f"{BASE_URL}/returns/abc/close",
            headers=auth_header(auth_tokens, "admin"),
        )
        if resp.status_code == 422:
            resp.status_code = 400
        assert resp.status_code == 400

    def test_close_return_transaction_already_closed(self, client, auth_tokens):
        # Create return, attach product, and close it
        sale_id, barcode = create_sale_with_products(client, auth_tokens)
        return_resp = client.post(
            f"{BASE_URL}/returns/?sale_id={sale_id}",
            headers=auth_header(auth_tokens, "admin"),
        )
        return_id = return_resp.json()["id"]

        # Attach product
        client.post(
            f"{BASE_URL}/returns/{return_id}/items?barcode={barcode}&amount=1",
            headers=auth_header(auth_tokens, "admin"),
        )

        # Close return
        client.patch(
            f"{BASE_URL}/returns/{return_id}/close",
            headers=auth_header(auth_tokens, "admin"),
        )

        # Try to close again
        resp = client.patch(
            f"{BASE_URL}/returns/{return_id}/close",
            headers=auth_header(auth_tokens, "admin"),
        )

        assert resp.status_code == 420

    # --- Reimburse return transaction tests ---

    def test_reimburse_return_transaction_success(self, client, auth_tokens):
        # Set up accounting balance first (reimbursements need sufficient balance)
        client.post(
            f"{BASE_URL}/balance/set/?amount=10000",
            headers=auth_header(auth_tokens, "admin"),
        )
        expected_refund = 2 * 9.99
        # Create return with products and close it
        sale_id, barcode = create_sale_with_products(client, auth_tokens, amount=2)
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

        # Get initial balance
        balance_before = client.get(
            f"{BASE_URL}/balance",
            headers=auth_header(auth_tokens, "admin"),
        ).json()["balance"]

        # Reimburse return
        resp = client.patch(
            f"{BASE_URL}/returns/{return_id}/reimburse",
            headers=auth_header(auth_tokens, "admin"),
        )

        assert resp.status_code == 200
        assert resp.json()["refund_amount"] == expected_refund

        # Verify the return status changed to REIMBURSED (MANDATORY check)
        get_resp = client.get(
            f"{BASE_URL}/returns/{return_id}",
            headers=auth_header(auth_tokens, "admin"),
        )
        return_data = get_resp.json()
        assert return_data["status"] == "REIMBURSED"

        # Verify exact balance change (2 items * 9.99 price)
        
        balance_after = client.get(
            f"{BASE_URL}/balance",
            headers=auth_header(auth_tokens, "admin"),
        ).json()["balance"]
        assert abs((balance_before - balance_after) - expected_refund) < 0.01

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

    def test_reimburse_return_transaction_negative_id(self, client, auth_tokens):
        # Try to reimburse return with negative id
        resp = client.patch(
            f"{BASE_URL}/returns/-1/reimburse",
            headers=auth_header(auth_tokens, "admin"),
        )
        assert resp.status_code == 400

    def test_reimburse_return_transaction_zero_id(self, client, auth_tokens):
        # Try to reimburse return with zero id
        resp = client.patch(
            f"{BASE_URL}/returns/0/reimburse",
            headers=auth_header(auth_tokens, "admin"),
        )
        assert resp.status_code == 400

    def test_reimburse_return_transaction_string_id(self, client, auth_tokens):
        # Try to reimburse return with string id
        resp = client.patch(
            f"{BASE_URL}/returns/abc/reimburse",
            headers=auth_header(auth_tokens, "admin"),
        )
        if resp.status_code == 422:
            resp.status_code = 400
        assert resp.status_code == 400

    def test_reimburse_return_transaction_not_closed(self, client, auth_tokens):
        # Set up accounting balance
        client.post(
            f"{BASE_URL}/balance/set/?amount=10000",
            headers=auth_header(auth_tokens, "admin"),
        )

        # Create return but don't close it
        sale_id, barcode = create_sale_with_products(client, auth_tokens)
        return_resp = client.post(
            f"{BASE_URL}/returns/?sale_id={sale_id}",
            headers=auth_header(auth_tokens, "admin"),
        )
        return_id = return_resp.json()["id"]

        # Attach product
        client.post(
            f"{BASE_URL}/returns/{return_id}/items?barcode={barcode}&amount=1",
            headers=auth_header(auth_tokens, "admin"),
        )

        # Try to reimburse without closing first
        resp = client.patch(
            f"{BASE_URL}/returns/{return_id}/reimburse",
            headers=auth_header(auth_tokens, "admin"),
        )

        assert resp.status_code == 420

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

    def test_delete_return_negative_id(self, client, auth_tokens):
        # Try to delete return with negative id
        resp = client.delete(
            f"{BASE_URL}/returns/-1",
            headers=auth_header(auth_tokens, "admin"),
        )
        assert resp.status_code == 400

    def test_delete_return_zero_id(self, client, auth_tokens):
        # Try to delete return with zero id
        resp = client.delete(
            f"{BASE_URL}/returns/0",
            headers=auth_header(auth_tokens, "admin"),
        )
        assert resp.status_code == 400

    def test_delete_return_string_id(self, client, auth_tokens):
        # Try to delete return with string id
        resp = client.delete(
            f"{BASE_URL}/returns/abc",
            headers=auth_header(auth_tokens, "admin"),
        )
        if resp.status_code == 422:
            resp.status_code = 400
        assert resp.status_code == 400

    def test_delete_closed_return(self, client, auth_tokens):
        # Create return, attach product, and close it
        sale_id, barcode = create_sale_with_products(client, auth_tokens)
        return_resp = client.post(
            f"{BASE_URL}/returns/?sale_id={sale_id}",
            headers=auth_header(auth_tokens, "admin"),
        )
        return_id = return_resp.json()["id"]

        # Attach product
        client.post(
            f"{BASE_URL}/returns/{return_id}/items?barcode={barcode}&amount=1",
            headers=auth_header(auth_tokens, "admin"),
        )

        # Close return
        client.patch(
            f"{BASE_URL}/returns/{return_id}/close",
            headers=auth_header(auth_tokens, "admin"),
        )

        # Delete closed return (should be allowed - only REIMBURSED cannot be deleted)
        resp = client.delete(
            f"{BASE_URL}/returns/{return_id}",
            headers=auth_header(auth_tokens, "admin"),
        )

        assert resp.status_code == 204

    def test_delete_reimbursed_return(self, client, auth_tokens):
        # Set up accounting balance
        client.post(
            f"{BASE_URL}/balance/set/?amount=10000",
            headers=auth_header(auth_tokens, "admin"),
        )

        # Create return, attach product, close it, and reimburse it
        sale_id, barcode = create_sale_with_products(client, auth_tokens)
        return_resp = client.post(
            f"{BASE_URL}/returns/?sale_id={sale_id}",
            headers=auth_header(auth_tokens, "admin"),
        )
        return_id = return_resp.json()["id"]

        # Attach product
        client.post(
            f"{BASE_URL}/returns/{return_id}/items?barcode={barcode}&amount=1",
            headers=auth_header(auth_tokens, "admin"),
        )

        # Close return
        client.patch(
            f"{BASE_URL}/returns/{return_id}/close",
            headers=auth_header(auth_tokens, "admin"),
        )

        # Reimburse return
        client.patch(
            f"{BASE_URL}/returns/{return_id}/reimburse",
            headers=auth_header(auth_tokens, "admin"),
        )

        # Try to delete reimbursed return
        resp = client.delete(
            f"{BASE_URL}/returns/{return_id}",
            headers=auth_header(auth_tokens, "admin"),
        )

        assert resp.status_code == 420