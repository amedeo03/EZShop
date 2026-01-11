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


class TestAccountingRouter:

    @pytest.mark.parametrize(
        "role, expected_exception_code",
        [
            ("admin", 200),  # success
            ("cashier", 403),  # unauthorized - insuff. rights
            ("shop_manager", 403),  # unauthorized - insuff. rights
            (None, 401),  # unauthenticated
        ],
    )
    def test_get_current_balance(
        self, client, auth_tokens, role, expected_exception_code
    ):

        headers = auth_header(auth_tokens, role) if role else None
        resp = client.get(
            BASE_URL + "/balance",
            headers=headers,
        )
        assert resp.status_code == expected_exception_code
        payload = resp.json()
        if role == "admin":
            assert payload["balance"] == 0

    @pytest.mark.parametrize(
        "role, expected_exception_code",
        [
            ("admin", 201),  # success
            ("cashier", 403),  # unauthorized - insuff. rights
            ("shop_manager", 403),  # unauthorized - insuff. rights
            (None, 401),  # unauthenticated
        ],
    )
    def test_set_balance_authentication(
        self, client, auth_tokens, role, expected_exception_code
    ):

        headers = auth_header(auth_tokens, role) if role else None
        resp = client.post(
            BASE_URL + "/balance/set/?amount=200",
            headers=headers,
        )
        assert resp.status_code == expected_exception_code
        payload = resp.json()
        if role == "admin":
            assert payload["success"] == True

    @pytest.mark.parametrize(
        "amount_to_set, expected_exception_code",
        [
            (10000, 201),  # success
            (-500, 421),  # negative amount
        ],
    )
    def test_set_balance_authenticated(
        self, client, auth_tokens, amount_to_set, expected_exception_code
    ):
        headers = auth_header(auth_tokens, "admin")
        resp = client.post(
            f"{BASE_URL}/balance/set/?amount={amount_to_set}",
            headers=headers,
        )
        assert resp.status_code == expected_exception_code

        if amount_to_set > 0:
            actual_balance_json = client.get(f"{BASE_URL}/balance", headers=headers)
            actual_balance = actual_balance_json.json()
            assert actual_balance["balance"] == amount_to_set

    @pytest.mark.parametrize(
        "role, expected_exception_code",
        [
            ("admin", 205),  # success
            ("cashier", 403),  # unauthorized - insuff. rights
            ("shop_manager", 403),  # unauthorized - insuff. rights
            (None, 401),  # unauthenticated
        ],
    )
    def test_reset_balance_authentication(
        self, client, auth_tokens, role, expected_exception_code
    ):

        headers = auth_header(auth_tokens, role) if role else None
        resp = client.post(
            BASE_URL + "/balance/reset",
            headers=headers,
        )
        assert resp.status_code == expected_exception_code

    def test_reset_balance_authenticated(self, client, auth_tokens):
        headers = auth_header(auth_tokens, "admin")

        client.post(
            f"{BASE_URL}/balance/set/?amount=1000",
            headers=headers,
        )
        new_balance_set = client.get(f"{BASE_URL}/balance", headers=headers)
        assert new_balance_set.json()["balance"] == 1000

        reset_balance_response = client.post(
            f"{BASE_URL}/balance/reset",
            headers=headers,
        )

        assert reset_balance_response.status_code == 205
        updated_balance = client.get(f"{BASE_URL}/balance", headers=headers)
        assert updated_balance.json()["balance"] == 0
