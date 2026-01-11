"""
End-to-end tests for customer routes.
Follows the pattern in tests/acceptance/user_test.py: uses TestClient and authenticates admin/manager/cashier.
"""

import asyncio
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
    # initialize/reset DB and create default users
    event_loop.run_until_complete(reset())
    event_loop.run_until_complete(init_db())

    users = {
        "admin": {"username": "admin", "password": "admin"},
        "manager": {"username": "ShopManager", "password": "ShManager"},
        "cashier": {"username": "Cashier", "password": "Cashier"},
    }

    tokens = {}
    for role, creds in users.items():
        resp = client.post(BASE_URL + "/auth", json=creds)
        assert resp.status_code == 200
        tokens[role] = f"Bearer {resp.json()['token']}"

    return tokens


def auth_header(tokens, role: str):
    return {"Authorization": tokens[role]}


# Sample payloads
CUSTOMER_SAMPLE = {"name": "John Doe", "card": None}
CUSTOMER_SAMPLE_2 = {"name": "Jane Smith", "card": None}
CUSTOMER_WITHOUT_NAME_SAMPLE = {"name": "", "card": None}
CUSTOMER_WITH_CARD = {"name": "Jane Smith", "card": {"card_id": "1234567890", "points": 0}}
CUSTOMER_UPDATE = {"name": "John Updated", "card": None}


# --- Create customer tests ---
@pytest.mark.parametrize(
        "role, customer_sample, expected_exception_code",
        [
            (
                "admin",
                {"name": "John Doe", "card": None},
                201,
            ),
            (
                "manager",
                {"name": "John Doe", "card": None},
                201,
            ),
            (
                "cashier",
                {"name": "John Doe", "card": None},
                201,
            ),
            (
                "admin",
                {"name": "John Doe", "card": {"card_id": "0000000001", "points": 10}},
                201,
            ),
            ( # unauthorized roles
                None,
                {"name": "John Doe", "card": None},
                401,
            ),
            ( # customer sample without name
                "admin",
                {"name": "", "card": None},
                400,
            ),
        ]
)
def test_create_customer(
    client, auth_tokens, role, customer_sample, expected_exception_code
    ):
    headers = auth_header(auth_tokens, role) if role else None

    resp = client.post(BASE_URL + "/customers", json=customer_sample, headers=headers)
        
    if expected_exception_code == 400:
        assert resp.status_code in (expected_exception_code, 422)
    else:
        assert resp.status_code == expected_exception_code
            
    
    data = resp.json()
    if expected_exception_code not in  (400, 401):
        assert data["name"] == customer_sample["name"]
        assert "id" in data




# --- List customers ---
@pytest.mark.parametrize(
        "role, expected_exception_code",
        [
            (
                "admin",
                200,
            ),
            (
                "cashier",
                200,
            ),
            (
                "manager",
                200,
            ),
            (
                None,
                401,
            ),
        ]
)
def test_list_customers(client, auth_tokens, role, expected_exception_code):
    headers = auth_header(auth_tokens, role) if role else None
    # ensure at least one customer exists
    client.post(BASE_URL + "/customers", json={"name": "List Test", "card": None}, headers=auth_header(auth_tokens, "admin"))
    
    resp = client.get(BASE_URL + "/customers", headers=headers)
    assert resp.status_code == expected_exception_code
    
    if expected_exception_code != 401:
        data = resp.json()
        assert isinstance(data, list)
        assert any(c.get("name") == "List Test" for c in data)
    



# --- Get customer ---
@pytest.mark.parametrize(
        "role, customer, customer_id, expected_exception_code",
        [
            (
                "admin",
                {"id": 1, "name": "John Doe", "card": None},
                1,
                200,
            ),
            (
                "cashier",
                {"id": 1, "name": "John Doe", "card": None},
                1,
                200,
            ),
            (
                "manager",
                {"id": 1, "name": "John Doe", "card": None},
                1,
                200,
            ),
            ( # unauthorized roles
                None,
                {"id": 1, "name": "John Doe", "card": None},
                1,
                401,
            ),
            ( # customer not found
                "admin",
                {"id": 1, "name": "John Doe", "card": None},
                999,
                404,
            ),
        ]
)
def test_get_customer(client, auth_tokens, role, customer, customer_id, expected_exception_code):
    
    headers = auth_header(auth_tokens, role) if role else None

    
    create = client.post(BASE_URL + "/customers", json=customer, headers=auth_header(auth_tokens, "admin"))
    #cid = customer_id #customer["id"] # create.json()["id"]
    
    resp = client.get(f"{BASE_URL}/customers/{customer_id}", headers=headers)
    assert resp.status_code == expected_exception_code
    if expected_exception_code not in (401, 404):
        assert resp.json()["id"] == customer_id



# --- Update customer ---
@pytest.mark.parametrize(
        "role, customer, customer_update, create_card, customer_id, expected_exception_code",
        [
            (
                "admin",
                {"id": 1, "name": "John Doe", "card": None},
                {"id": 1, "name": "John Update", "card": None},
                False,
                1,
                201,
            ),
            (
                "cashier",
                {"id": 1, "name": "John Doe", "card": None},
                {"id": 1, "name": "John Update", "card": None},
                False,
                1,
                201,
            ),
            (
                "manager",
                {"id": 1, "name": "John Doe", "card": None},
                {"id": 1, "name": "John Update", "card": None},
                False,
                1,
                201,
            ),
            ( # customer update with card
                "admin",
                {"id": 1, "name": "John Doe", "card": {'card_id': '0000000000', 'points': 0}},
                {"id": 1, "name": "John Update", "card": None},
                True,
                1,
                201,
            ),
            ( # update customer -> detach card
                "admin",
                {"id": 1, "name": "John Doe", "card": {"card_id": "0000000001", "points": 0}},
                {"id": 1, "name": "John Update", "card": {"card_id": "", "points": 0}},
                False,
                1,
                201,
            ),
            ( # unauthorized roles
                None,
                {"id": 1, "name": "John Doe", "card": None},
                {"id": 1, "name": "John Update", "card": None},
                False,
                1,
                401,
            ),
            ( # customer not found
                "admin",
                {"id": 1, "name": "John Doe", "card": None},
                {"id": 1, "name": "John Update", "card": None},
                False,
                999,
                404,
            ),
            ( # card not found
                "admin",
                {"id": 1, "name": "John Doe", "card": {"card_id": "99999999999", "points": 10}},
                {"id": 1, "name": "John Update", "card": {"card_id": "99999999999", "points": 10}},
                False,
                1,
                404,
            ),
            ( # empty customer name
                "admin",
                {"id": 1, "name": "", "card": None},
                {"id": 1, "name": "", "card": None},
                False,
                1,
                400,
            ),
            
        ]
)
def test_update_customer(client, auth_tokens, role, customer, customer_update,create_card, customer_id, expected_exception_code):
    headers = auth_header(auth_tokens, role) if role else None
    # create customer
    create = client.post(BASE_URL + "/customers", json=customer, headers=auth_header(auth_tokens, "admin"))
    if create_card:
        # create card
        card_resp = client.post(BASE_URL + "/customers/cards", headers=auth_header(auth_tokens, "admin"))
        card_id = card_resp.json()["card_id"]
        # attach
        attach = client.patch(f"{BASE_URL}/customers/{customer_id}/attach-card/{card_id}", headers=auth_header(auth_tokens, "admin"))
   

    resp = client.put(f"{BASE_URL}/customers/{customer_id}", json=customer_update, headers=headers)
    
    if expected_exception_code == 400:
        assert resp.status_code in (expected_exception_code, 422)
    else:
        assert resp.status_code == expected_exception_code
    
    
    if expected_exception_code not in (400, 401, 404):
        assert resp.json()["name"] == customer_update["name"]
  
        if customer_update["card"] is not None and customer_update["card"]["card_id"] == "":
            assert resp.json()["card"] is None
        else:
            assert resp.json()["card"] == customer["card"]
    




    

# --- Delete customer ---
@pytest.mark.parametrize(
        "role, customer, customer_id, expected_exception_code",
        [
            (
                "admin",
                {"id": 1, "name": "John Doe", "card": None},
                1,
                204,
            ),
            (
                "cashier",
                {"id": 2, "name": "John Doe", "card": None},
                2,
                204,
            ),
            (
                "manager",
                {"id": 3, "name": "John Doe", "card": None},
                3,
                204,
            ),
            (
                None,
                {"id": 1, "name": "John Doe", "card": None},
                1,
                401,
            ),
            ( # not found
                "admin",
                {"id": 1, "name": "John Doe", "card": None},
                999,
                404,
            ),
        ]
)
def test_delete_customer(client, auth_tokens, role, customer, customer_id, expected_exception_code):
    
    headers = auth_header(auth_tokens, role) if role else None
    # create customer
    r = client.post(BASE_URL + "/customers", json=customer, headers=auth_header(auth_tokens, "admin"))
    
    # delete customer
    resp = client.delete(f"{BASE_URL}/customers/{customer_id}", headers=headers)
    
    assert resp.status_code == expected_exception_code
    
    # verify gone
    get_resp = client.get(f"{BASE_URL}/customers/{customer_id}", headers=auth_header(auth_tokens, "admin"))
    assert get_resp.status_code == 404

@pytest.mark.parametrize(
        "role, customer, customer_id, expected_exception_code",
        [
            (
                "admin",
                {"id": 5, "name": "John Doe", "card": None},
                5,
                404,
            ),
        ]
)
def test_delete_customer_with_card(client, auth_tokens, role, customer, customer_id, expected_exception_code):
    
    headers = auth_header(auth_tokens, role) if role else None
    # create customer
    create = client.post(BASE_URL + "/customers", json=customer, headers=auth_header(auth_tokens, "admin"))
    # create card
    card_resp = client.post(BASE_URL + "/customers/cards", headers=auth_header(auth_tokens, "admin"))
    assert card_resp.status_code == 201
    card_id = card_resp.json()["card_id"]
    # attach
    attach = client.patch(f"{BASE_URL}/customers/{customer_id}/attach-card/{card_id}", headers=auth_header(auth_tokens, "admin"))
    assert attach.status_code == 201
    
    
    resp = client.delete(f"{BASE_URL}/customers/{customer_id}", headers=headers)
    assert resp.status_code == 204
    
    # verify card is also gone
    card_resp = client.patch(f"{BASE_URL}/customers/cards/{card_id}", params={"points": 42}, headers=auth_header(auth_tokens, "admin"))
    assert card_resp.status_code == expected_exception_code
     



# --- Card management ---
@pytest.mark.parametrize(
        "role, expected_exception_code",
        [
            (
                "admin",
                201,
            ),
            (
                "cashier",
                201,
            ),
            (
                "manager",
                201,
            ),
            (
                None,
                401,
            ),
        ]
)
def test_create_card(client, auth_tokens, role, expected_exception_code):
    # create card
    headers = auth_header(auth_tokens, role) if role else None

    card_resp = client.post(BASE_URL + "/customers/cards", headers=headers)
    assert card_resp.status_code == expected_exception_code
    


@pytest.mark.parametrize(
        "role, customer, invalid_card_id, card_not_found,  expected_exception_code",
        [
            (
                "admin",
                {"id": 7, "name": "John Doe", "card": None},
                False,
                False,
                201,
            ),
            (
                "cashier",
                {"id": 8, "name": "John Doe", "card": None},
                False,
                False,
                201,
            ),
            (
                "manager",
                {"id": 9, "name": "John Doe", "card": None},
                False,
                False,
                201,
            ),
            (
                None,
                {"id": 10, "name": "John Doe", "card": None},
                False,
                False,
                401,
            ),
            (
                "admin",
                {"id": 10, "name": "John Doe", "card": None},
                True,
                False,
                400,
            ),
            (
                "admin",
                {"id": 10, "name": "John Doe", "card": None},
                False,
                True,
                404,
            ),
        ]
)
def test_attach_card(client, auth_tokens, role, customer,invalid_card_id, card_not_found, expected_exception_code):
    
    headers = auth_header(auth_tokens, role) if role else None
    
    # create customer
    create = client.post(BASE_URL + "/customers", json=customer, headers=auth_header(auth_tokens, "admin"))
    cid = create.json()["id"]
    # create card
    card_resp = client.post(BASE_URL + "/customers/cards", headers=auth_header(auth_tokens, "admin"))
    assert card_resp.status_code == 201
    card_id = card_resp.json()["card_id"]
    if invalid_card_id:
        card_id = "abc"  # non-existing card id for negative test
    elif card_not_found:
        card_id = "9999999999"  # non-existing card id for negative test
    # attach
    attach = client.patch(f"{BASE_URL}/customers/{cid}/attach-card/{card_id}", headers=headers)
    assert attach.status_code == expected_exception_code
    
    if expected_exception_code not in (400, 401, 404):
        
        data = attach.json()
        assert data.get("card") is not None
        assert data["card"]["card_id"] == card_id
        assert data["card"]["points"] == 0
    
    
def test_attach_card_already_attached(client, auth_tokens):
    card_resp = client.post(BASE_URL + "/customers/cards", headers=auth_header(auth_tokens, "admin"))
    create_1 = client.post(BASE_URL + "/customers", json=CUSTOMER_SAMPLE, headers=auth_header(auth_tokens, "admin"))
    create_2 = client.post(BASE_URL + "/customers", json=CUSTOMER_SAMPLE_2, headers=auth_header(auth_tokens, "admin"))

    card_id = card_resp.json()["card_id"]
    cid_1 = create_1.json()["id"]
    cid_2 = create_2.json()["id"]

    attach = client.patch(f"{BASE_URL}/customers/{cid_1}/attach-card/{card_id}", headers=auth_header(auth_tokens, "admin"))
    assert attach.status_code == 201
    
    attach_to_other_customer = client.patch(f"{BASE_URL}/customers/{cid_2}/attach-card/{card_id}", headers=auth_header(auth_tokens, "admin"))

    assert attach_to_other_customer.status_code == 409




@pytest.mark.parametrize(
        "role, points, invalid_card, card_not_found,  expected_exception_code",
        [
            (
                "admin",
                50,
                False,
                False,
                201,
            ),
            (
                "cashier",
                50,
                False,
                False,
                201,
            ),
            (
                "manager",
                50,
                False,
                False,
                201,
            ),
            ( # unauthenticated
                None,
                50,
                False,
                False,
                401,
            ),
            (
                "admin",
                50,
                True,
                False,
                400,
            ),
            (
                "admin",
                50,
                False,
                True,
                404,
            ),
            ( # insufficient points
                "admin",
                -1,
                False,
                False,
                400,
            ),
        ]
)
def test_modify_points(client, auth_tokens, role, points, invalid_card, card_not_found, expected_exception_code):
    
    headers = auth_header(auth_tokens, role) if role else None
 
    # create card
    card_resp = client.post(BASE_URL + "/customers/cards", headers=auth_header(auth_tokens, "admin"))
    card_id = card_resp.json()["card_id"]
    
    if invalid_card:
        card_id = "abc"
        
    if card_not_found:
        card_id = "9999999999"
    # modify

    resp = client.patch(f"{BASE_URL}/customers/cards/{card_id}", params={"points": points}, headers=headers)

    if expected_exception_code == 400:
        assert resp.status_code in (expected_exception_code, 422)
    else:
        assert resp.status_code == expected_exception_code
    
    if expected_exception_code not in (400, 401, 404):
        assert resp.json()["points"] == points



