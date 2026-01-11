from fastapi.testclient import TestClient
from httpx import AsyncClient
from app.config.config import ROUTES
from main import app
from unittest.mock import patch, AsyncMock
from init_db import init_db, reset
import pytest
import asyncio
from datetime import datetime, timezone


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
def client():
    from main import app
    with TestClient(app) as c:
        yield c

BASE_URL = "http://127.0.0.1:8000/api/v1"
START_TEST=datetime.now(timezone.utc).replace( 
                    microsecond=0
                )
NEW_SALES={
                "id": 1,
                "status": "OPEN",
                "discount_rate": 0.05,
                "created_at": "2025-10-30T12:34:56Z",
                "closed_at": "2025-10-31T12:34:56Z",
                "lines": [
                    {
                    "id": 1,
                    "sale_id": 10,
                    "product_barcode": "0123456789",
                    "quantity": 2,
                    "price_per_unit": 5.5,
                    "discount_rate": 0.1
                    }
                    ]
                }
LIST_ALL_SALES=[
    {
                "id": 10,
                "status": "OPEN",
                "discount_rate": 0.05,
                "created_at": "2025-10-30T12:34:56Z",
                "closed_at": "2025-10-31T12:34:56Z",
                "lines": [
                    {
                    "id": 1,
                    "sale_id": 10,
                    "product_barcode": "0123456789",
                    "quantity": 2,
                    "price_per_unit": 5.5,
                    "discount_rate": 0.1
                    }
                    ]
                },
                {
                "id": 10,
                "status": "OPEN",
                "discount_rate": 0.06,
                "created_at": "2025-11-29T12:34:56Z",
                "closed_at": "2025-11-20T12:34:56Z",
                "lines": [
                    {
                    "id": 1,
                    "sale_id": 10,
                    "product_barcode": "0123456789",
                    "quantity": 2,
                    "price_per_unit": 5.5,
                    "discount_rate": 0.1
                    }
                    ]
                }
]
PAID_SALE={
                "id": 2,
                "status": "PAID",
                "discount_rate": 0.05,
                "created_at": "2025-10-30T12:34:56Z",
                "closed_at": "2025-10-31T12:34:56Z",
                "lines": [
                    {
                    "id": 1,
                    "sale_id": 2,
                    "product_barcode": "0123456789",
                    "quantity": 2,
                    "price_per_unit": 5.5,
                    "discount_rate": 0.1
                    }
                    ]
                }

CLOSE_SALES={
                "id": 3,
                "status": "PENDING",
                "discount_rate": 0.05,
                "created_at": "2025-10-30T12:34:56Z",
                "closed_at": "2025-10-31T12:34:56Z",
                "lines": [
                    {
                    "id": 1,
                    "sale_id": 10,
                    "product_barcode": "0123456789",
                    "quantity": 2,
                    "price_per_unit": 5.5,
                    "discount_rate": 0.1
                    }
                    ]
                }
FIRST_PRODUCT={
                    "description": "updated product",
                    "barcode": "9780201379624",
                    "price_per_unit": 9.99,
                    "note": "updated note",
                    "quantity": 1000,
                    "position": "B-1-1"
                }
SECOND_PRODUCT={
                    "description": "updated product",
                    "barcode": "0000000000000",
                    "price_per_unit": 9.99,
                    "note": "updated note",
                    "quantity": 1000,
                    "position": "B-1-1"
                }
INVALID_ERROR={
  "code": 420,
  "message": "Sale not found",
  "name": "NotFoundError"
}
BOOLEAN_RESPONSE={"success": True}
CHANGE_RESPONSE={"change": 5}
POINT_RESPONSE={"points": 15}

@pytest.fixture(scope="session", autouse=True)
def auth_tokens(event_loop, client):
    """Authenticate users once and return their JWT tokens."""

    event_loop.run_until_complete(reset())
    event_loop.run_until_complete(init_db())
    users = {
        "admin": {"username": "admin", "password": "admin"},
        "manager": {"username": "ShopManager", "password": "ShManager"},
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

@pytest.mark.parametrize(
        "role, new_sale, expected_exception_code",
    [("admin",{
        "id":1,
        "status":"OPEN",
        "discount_rate":0.0
        }, 201),("cashier",{
        "id":1,
        "status":"OPEN",
        "discount_rate":0.0
        }, 201),("cashier",{
        "id":1,
        "status":"OPEN",
        "discount_rate":0.0
        }, 201),
     (None,{}, 401)]
)
def test_create_sale_route(client,auth_tokens,role, new_sale, expected_exception_code):
    headers=auth_header(auth_tokens,role) if role else None
    resp = client.post(
            BASE_URL + "/sales",
            headers=headers,
        )
    assert resp.status_code==expected_exception_code
    if resp.status_code==201 and "admin"==role:
        resp=resp.json()
        assert resp["id"]== 1
        assert resp["status"]=='OPEN'
        assert resp["created_at"]>=str(START_TEST)
        assert resp["discount_rate"]==0.0
        assert resp["lines"]==[]
    
@pytest.mark.parametrize(
        "role, expected_exception_code",
        [
            ("admin", 200),  # success
            ("manager", 200),  # success
            ("cashier", 200),  # success
            (None, 401),  # unauthenticated
        ],
    )
def test_get_all_sales_route(client,auth_tokens,role,expected_exception_code):
    headers=auth_header(auth_tokens,role) if role else None
    resp = client.get(
            BASE_URL + "/sales/",
            headers=headers,
        )
    assert resp.status_code==expected_exception_code
    if role=="admin":
        for r in resp.json():
            re=client.delete(
                BASE_URL+"/sales/"+str(r["id"]),
                headers=headers,
            )
        resp = client.get(
            BASE_URL + "/sales/",
            headers=headers,
            )
        client.post(
            BASE_URL + "/sales",
            headers=headers,
        )
        resp=resp.json()
        assert resp==[]
        client.post(
            BASE_URL+"/products",
            json=FIRST_PRODUCT,
            headers=headers
        )
        client.post(
             BASE_URL+"/sales/1/items/?barcode="+FIRST_PRODUCT["barcode"]+"amount=1"
            , headers=headers
        )
        resp = client.get(
            BASE_URL + "/sales/",
            headers=headers,
        )
        resp=resp.json()
        for r in resp:
            assert r["id"]== 1
            assert r["status"]=='OPEN'
            assert r["created_at"]>=str(START_TEST)
            assert r["discount_rate"]==0.0
            for rl in r["lines"]:
                rl["id"]==1
                rl["sale_id"]==1
                rl["product_barcode"]==FIRST_PRODUCT["barcode"]
                rl["quantity"]==1
                rl["price_per_unit"]==FIRST_PRODUCT["price_per_unit"]
                rl["discount_rate"]==0.0

        

@pytest.mark.parametrize(
        "input_id, role, expected_exception_code",
        [
            (1, "admin", 200),  # success
            (-1, "manager", 400),  # invalid id
            (12345, "cashier", 404),  # no product found
            ("abc", "admin", 400),  # invalid id
            (1, None, 401),  # unauthenticated
        ],
    )
def test_get_sale_id_route_ok(client,auth_tokens,input_id, role, expected_exception_code):
    headers = auth_header(auth_tokens, role) if role else None
    client.post(
            BASE_URL + "/sales",
            json=NEW_SALES,
            headers=headers,
        )
    if role=="admin":
        client.post(
            BASE_URL+"/products",
            json=FIRST_PRODUCT,
            headers=headers
        )
        client.post(
             BASE_URL+"/sales/1/items/?barcode="+FIRST_PRODUCT["barcode"]+"amount=1"
            ,headers=headers
        )
        resp = client.get(
            BASE_URL + "/sales/",
            headers=headers,
        )
        resp=resp.json()
        

    resp = client.get(
            BASE_URL + "/sales/" + str(input_id),
            headers=headers,
        )
    
    if expected_exception_code == 400:
            assert resp.status_code in (expected_exception_code, 422)
    else:
            assert resp.status_code == expected_exception_code
    if expected_exception_code==201:
        for r in resp:
            assert r["id"]== 1
            assert r["status"]=='OPEN'
            assert r["created_at"]>=str(START_TEST)
            assert r["discount_rate"]==0.0
            for rl in r["lines"]:
                rl["id"]==1
                rl["sale_id"]==1
                rl["product_barcode"]==FIRST_PRODUCT["barcode"]
                rl["quantity"]==1
                rl["price_per_unit"]==FIRST_PRODUCT["price_per_unit"]
                rl["discount_rate"]==0.0


@pytest.mark.parametrize(
        "input_id, role, exception_code",
        [
            (1, "admin", 204),  # success
            (-1, "manager", 400),  # invalid id
            (12345, "cashier", 404),  # no product found
            ("abc", "admin", 400),  # invalid id
            (1, None, 401),  # unauthenticated
            (2, "admin", 420)
        ],
    )
def test_delete_sale_route(client,auth_tokens,role,input_id,exception_code):
        headers = auth_header(auth_tokens, role) if role else None
        client.post(
            BASE_URL + "/sales",
            headers=headers,
        )
        result=client.post(
            BASE_URL + "/sales",
            headers=headers,
        )

        if role=="admin":
            client.post(
                BASE_URL+"/products",
                json=FIRST_PRODUCT,
                headers=headers
            )

            client.post(
             BASE_URL+"/sales/2/items?barcode="
             +FIRST_PRODUCT["barcode"]+"&amount=2"
            ,headers=headers
            )
            
            client.patch(
                BASE_URL + "/sales/2/close",
                headers=headers,
            )
            client.patch(
                BASE_URL + "/sales/2/pay/?cash_amount=10000",
                headers=headers,
            )

        resp=client.delete(
             BASE_URL+"/sales/"+str(input_id),
             headers=headers)
        
        if exception_code == 400:
            assert resp.status_code in (exception_code, 422)
        else:
            assert resp.status_code == exception_code


@pytest.mark.parametrize(
        "input_id, role, exception_code,stack,barcode",
        [
            (3, "admin", 201,1,FIRST_PRODUCT["barcode"]),  # success
            (-1, "manager", 400,1,FIRST_PRODUCT["barcode"]),  # invalid id
            (12345, "cashier", 404,1,FIRST_PRODUCT["barcode"]),  # no product found
            ("abc", "admin", 400,1,FIRST_PRODUCT["barcode"]),  # invalid id
            (3, None, 401,1,FIRST_PRODUCT["barcode"]),  # unauthenticated
            (3, "admin", 400,1,"000"),
            (3, "admin", 400,1,""),
            (4, "admin", 400,8000000,FIRST_PRODUCT["barcode"]),
            (4, "admin", 400,-80,FIRST_PRODUCT["barcode"]),
            (3, "cashier", 420,1,FIRST_PRODUCT["barcode"])
        ],
    )
def test_product_added_route(client,auth_tokens,input_id, role, exception_code,stack,barcode):
    headers = auth_header(auth_tokens, role) if role else None
    client.post(
                BASE_URL+"/products",
                json=FIRST_PRODUCT,
                headers=headers
            )
    client.post(
            BASE_URL + "/sales",
            headers=headers,
        )
    client.post(
            BASE_URL + "/sales",
            headers=headers,
        )
    client.post(
            BASE_URL + "/sales",
            headers=headers,
        )
    resp=client.post(
            BASE_URL + "/sales/"+str(input_id)+"/items/?barcode="
            +barcode+"&amount="+str(stack),
            headers=headers,
        )
    if exception_code == 400 or resp.status_code==409:
        assert resp.status_code in (exception_code, 422,409)
    else:
        assert resp.status_code == exception_code
    if resp.status_code==201:
        assert resp.json()["success"]

    if role=="cashier" and input_id!=12345:
            client.patch(
                BASE_URL + "/sales/3/close",
                headers=headers,
            )
            resp=client.post(
                BASE_URL + "/sales/"+str(input_id)+"/items/?barcode="
                +barcode+"&amount="+str(stack),
                headers=headers,
            )
            assert resp.status_code==420
            client.patch(
                BASE_URL + "/sales/3/pay/?cash_amount=10000",
                headers=headers,
            )
            assert resp.status_code==420
    
@pytest.mark.parametrize(
        "input_id, role, exception_code,stack,barcode",
        [
            (4, "admin", 202,1,FIRST_PRODUCT["barcode"]),  # success
            (4, "manager", 202,-1,FIRST_PRODUCT["barcode"]),
            (4, "manager", 202,-2,FIRST_PRODUCT["barcode"]),
            (12345, "admin", 404,1,FIRST_PRODUCT["barcode"]),
            (-1, "admin", 400,1,FIRST_PRODUCT["barcode"]),  # no product found
            ("abc", "admin", 400,1,FIRST_PRODUCT["barcode"]),  # invalid id
            (4, None, 401,1,FIRST_PRODUCT["barcode"]),  # unauthenticated
            (4, "admin", 400,1,"000"),
            (4, "admin", 400,1,""),
            (4, "admin", 400,8000000,FIRST_PRODUCT["barcode"]),
            (4, "admin", 400,-80,FIRST_PRODUCT["barcode"]),
            (4, "cashier", 202,1,FIRST_PRODUCT["barcode"])
        ],
    )
def test_remove_product_route_ok(client,auth_tokens,input_id, role, exception_code,stack,barcode):
    headers = auth_header(auth_tokens, role) if role else None
    client.post(
                BASE_URL+"/products",
                json=FIRST_PRODUCT,
                headers=headers
            )
    for i in range(4):
        client.post(
            BASE_URL + "/sales",
            headers=headers,
        )
    client.post(
            BASE_URL + "/sales/"+str(input_id)+"/items/?barcode="
            +FIRST_PRODUCT["barcode"]+"&amount=1",
            headers=headers,
        )
    resp = client.get(
            BASE_URL + "/sales/" + str(input_id),
            headers=headers,
        )
    if resp.status_code==201:
        q=resp.json()["lines"][0]["quantity"]
    else:
        q=0
    if role=="admin" or role=="cashier":
        resp=client.delete(
             BASE_URL+"/sales/"+str(input_id)+"/items/?barcode="+
             barcode+"&amount="+str(stack),
             headers=headers)
    elif role=="manager":
         if stack==-2 and q<-stack:
            resp=client.delete(
                BASE_URL+"/sales/"+str(input_id)+"/items/?barcode="+
                barcode+"&amount=-1",
                headers=headers)
         else:
            resp=client.delete(
                BASE_URL+"/sales/"+str(input_id)+"/items/?barcode="+
                barcode+"&amount="+str(stack),
                headers=headers)
        
    if exception_code == 400:
        assert resp.status_code in (exception_code, 422)
    else:
        assert resp.status_code == exception_code
    
    if exception_code==202:
        assert resp.json()["success"]

    if stack==-2:
         resp = client.get(
            BASE_URL + "/sales/" + str(input_id),
            headers=headers,
        )
         resp=resp.json()
         assert resp["lines"]==[]
    if role=="cashier":
            client.post(
                BASE_URL + "/sales/"+str(input_id)+"/items/?barcode="
                +FIRST_PRODUCT["barcode"]+"&amount=1",
                headers=headers,
            )
            client.patch(
                BASE_URL + "/sales/"+str(input_id)+"/close",
                headers=headers,
            )
            resp=client.delete(
                BASE_URL + "/sales/"+str(input_id)+"/items/?barcode="
                +barcode+"&amount="+str(stack),
                headers=headers,
            )
            assert resp.status_code==420
            client.patch(
                BASE_URL + "/sales/"+str(input_id)+"/pay/?cash_amount=10000",
                headers=headers,
            )
            resp=client.delete(
                BASE_URL + "/sales/"+str(input_id)+"/items/?barcode="
                +barcode+"&amount="+str(stack),
                headers=headers,
            )
            assert resp.status_code==420

@pytest.mark.parametrize(
        "input_id, role, exception_code, disc",
        [
            (5, "admin", 200,0.01),
            (-1,"admin",400,0.01),
            (5,"manager",400,2),
            (5,"admin",400,-0.5),
            (5,None,401,0.01),
            (15555,"admin",404,0.5),
            (5,"admin",420,0.02)
        ]
    )    
def test_set_discount_route(client,auth_tokens,input_id, role, exception_code, disc):
    headers = auth_header(auth_tokens, role) if role else None
    for i in range(5):
        client.post(
            BASE_URL + "/sales",
            headers=headers,
        )
    resp=client.patch(
        BASE_URL+"/sales/"+str(input_id)+"/discount?discount_rate="+str(disc),
        headers=headers)
    if exception_code == 400:
        assert resp.status_code in (exception_code, 422)
    elif exception_code!=420:
        assert resp.status_code == exception_code
    if exception_code==200:
        assert resp.json()["success"]
    
    if exception_code==420:
            client.post(
                BASE_URL+"/products",
                json=FIRST_PRODUCT,
                headers=headers
            )
            client.post(
                BASE_URL + "/sales/"+str(input_id)+"/items/?barcode="
                +FIRST_PRODUCT["barcode"]+"&amount=1",
                headers=headers,
            )
            client.patch(
                BASE_URL + "/sales/"+str(input_id)+"/close",
                headers=headers,
            )
            resp=client.patch(
                BASE_URL+"/sales/"+str(input_id)+"/discount?discount_rate="+str(disc),
                headers=headers)
            assert resp.status_code==420
            client.patch(
                BASE_URL + "/sales/"+str(input_id)+"/pay/?cash_amount=10000",
                headers=headers,
            )
            resp=client.patch(
                BASE_URL+"/sales/"+str(input_id)+"/discount?discount_rate="+str(disc),
                headers=headers
            )
            assert resp.status_code==420

@pytest.mark.parametrize(
        "input_id, role, exception_code, disc,barcode",
        [
            (6, "admin", 200,0.01,FIRST_PRODUCT["barcode"]),
            (-1,"admin",400,0.01,FIRST_PRODUCT["barcode"]),
            (6,"manager",400,2,FIRST_PRODUCT["barcode"]),
            (6,"admin",400,-0.5,FIRST_PRODUCT["barcode"]),
            (6, "admin", 400,0.1,"000"),
            (6,None,401,0.01,FIRST_PRODUCT["barcode"]),
            (15555,"admin",404,0.5,FIRST_PRODUCT["barcode"]),
            (6,"admin",420,0.02,FIRST_PRODUCT["barcode"])
        ]
    ) 
def test_set_discount_product_route(client,auth_tokens,input_id, role, exception_code, disc,barcode):
    headers = auth_header(auth_tokens, role) if role else None
    for i in range(6):
        client.post(
            BASE_URL + "/sales",
            headers=headers,
        )
    client.post(
                BASE_URL+"/products",
                json=FIRST_PRODUCT,
                headers=headers
            )
    client.post(
            BASE_URL + "/sales/"+str(input_id)+"/items/?barcode="
            +barcode+"&amount=1",
            headers=headers,
            )
    resp=client.patch(
        BASE_URL+"/sales/"+str(input_id)+"/items/"+barcode+
        "/discount?discount_rate="+str(disc),
        headers=headers)
    if exception_code == 400:
        assert resp.status_code in (exception_code, 422)
    elif exception_code!=420:
        assert resp.status_code == exception_code
    if exception_code==200:
        assert resp.json()["success"]
    
    if exception_code==420:
        client.patch(
            BASE_URL + "/sales/"+str(input_id)+"/close",
            headers=headers,
        )
        resp=client.patch(
            BASE_URL+"/sales/"+str(input_id)+"/items/"+barcode+
            "/discount?discount_rate="+str(disc),
            headers=headers)
        assert resp.status_code==420
        client.patch(
            BASE_URL + "/sales/"+str(input_id)+"/pay/?cash_amount=10000",
            headers=headers,
        )
        resp=client.patch(
            BASE_URL+"/sales/"+str(input_id)+"/items/"+barcode+
            "/discount?discount_rate="+str(disc),
            headers=headers)
        assert resp.status_code==420

@pytest.mark.parametrize(
        "input_id, role, exception_code",
        [
            (7, "admin", 200),
            (-1,"admin",400),
            (7,None,401),
            (15555,"admin",404),
            (7,"manager",420),
            (8,"cashier",200)
        ]
    ) 
def test_close_sale_route_ok(client,auth_tokens,input_id, role, exception_code):
    headers = auth_header(auth_tokens, role) if role else None
    for i in range(8):
        client.post(
            BASE_URL + "/sales",
            headers=headers,
        )
    client.post(
                BASE_URL+"/products",
                json=FIRST_PRODUCT,
                headers=headers
            )
    if input_id!=8:
        client.post(
                BASE_URL + "/sales/"+str(input_id)+"/items/?barcode="
                +FIRST_PRODUCT["barcode"]+"&amount=1",
                headers=headers,
                )
    resp=client.patch(BASE_URL+"/sales/"+str(input_id)+"/close",
            headers=headers)
    
    if exception_code == 400:
        assert resp.status_code in (exception_code, 422)
    elif exception_code!=420:
        assert resp.status_code == exception_code
    if exception_code==200:
        assert resp.json()["success"]
    
    if input_id==8:
        resp=client.get(BASE_URL+"sale"+str(input_id),headers=headers)
        assert resp.status_code==404

    if exception_code==420:
        resp=client.patch(BASE_URL+"/sales/"+str(input_id)+"/close",
            headers=headers)
        resp=client.patch(BASE_URL+"/sales/"+str(input_id)+"/close",
            headers=headers)
        assert exception_code==420
        client.patch(
            BASE_URL + "/sales/"+str(input_id)+"/pay/?cash_amount=10000",
            headers=headers,
        )
        resp=client.patch(BASE_URL+"/sales/"+str(input_id)+"/close",
            headers=headers)
        assert exception_code==420

@pytest.mark.parametrize(
        "input_id, role, exception_code,amount",
        [
            (9, "admin", 200,10000),
            (9, "admin", 400,-10000),
            (9, "admin", 420,1),
            (-1,"admin",400,10000),
            (9,None,401,10000),
            (15555,"admin",404,10000),
            (10,"manager",420,10000),
        ]
    ) 
def test_paid_sale_route(client,auth_tokens,input_id,amount, role, exception_code):
    headers = auth_header(auth_tokens, role) if role else None
    for i in range(9):
        client.post(
            BASE_URL + "/sales",
            headers=headers,
        )
    client.post(
                BASE_URL+"/products",
                json=FIRST_PRODUCT,
                headers=headers
            )
    client.post(
                BASE_URL+"/products",
                json=SECOND_PRODUCT,
                headers=headers
            )
    client.post(
            BASE_URL + "/sales/"+str(input_id)+"/items/?barcode="
            +FIRST_PRODUCT["barcode"]+"&amount=1",
            headers=headers,
            )
    client.post(
            BASE_URL + "/sales/"+str(input_id)+"/items/?barcode="
            +SECOND_PRODUCT["barcode"]+"&amount=1",
            headers=headers,
            )
    client.patch(
        BASE_URL+"/sales/"+str(input_id)+"/discount?discount_rate=0.02",
        headers=headers)
    client.patch(
        BASE_URL+"/sales/"+str(input_id)+"/items/"+SECOND_PRODUCT["barcode"]+
        "/discount?discount_rate=0.05",
        headers=headers)
    client.patch(BASE_URL+"/sales/"+str(input_id)+"/close",
            headers=headers)
    
    resp=client.patch(BASE_URL+"/sales/"+str(input_id)+"/pay/?cash_amount="+str(amount),
            headers=headers)
    if exception_code == 400:
        assert resp.status_code in (exception_code, 422)
    elif exception_code!=420:
        assert resp.status_code == exception_code
    elif amount==1:
        assert resp.status_code == exception_code
    if exception_code==200:
        assert resp.json()["change"]==9990.21
    
    if exception_code==420:
        client.post(
            BASE_URL + "/sales",
            headers=headers,
        )
        resp=client.patch(BASE_URL+"/sales/"+str(input_id)+"/pay/?cash_amount=10000",
            headers=headers)
        assert exception_code==420

        client.post(
            BASE_URL + "/sales/"+str(input_id)+"/items/?barcode="
            +SECOND_PRODUCT["barcode"]+"&amount=1",
            headers=headers,
            )
        client.patch(BASE_URL+"/sales/"+str(input_id)+"/close",
            headers=headers)
        resp=client.patch(BASE_URL+"/sales/"+str(input_id)+"/pay/?cash_amount=10000",
            headers=headers)
        resp=client.patch(BASE_URL+"/sales/"+str(input_id)+"/pay/?cash_amount=10000",
            headers=headers)
        assert exception_code==420

@pytest.mark.parametrize(
        "input_id, role, exception_code",
        [
            (11, "admin", 200),
            (-1,"admin",400),
            (11,None,401),
            (15555,"admin",404)
        ]
    ) 
def test_points_route_ok(client,auth_tokens,input_id, role, exception_code):
    headers = auth_header(auth_tokens, role) if role else None
    for i in range(11):
        client.post(
            BASE_URL + "/sales",
            headers=headers,
        )
    client.post(
                BASE_URL+"/products",
                json=FIRST_PRODUCT,
                headers=headers
            )
    client.post(
            BASE_URL + "/sales/"+str(input_id)+"/items/?barcode="
            +FIRST_PRODUCT["barcode"]+"&amount=10",
            headers=headers,
            )
    resp=client.get(BASE_URL+"/sales/"+str(input_id)+"/points",
                headers=headers)
    if exception_code==420:
        assert resp.status_code==420
    client.patch(BASE_URL+"/sales/"+str(input_id)+"/close",
            headers=headers)
    resp=client.get(BASE_URL+"/sales/"+str(input_id)+"/points",
                headers=headers)
    if exception_code==420:
        assert resp.status_code==420
    resp=client.patch(BASE_URL+"/sales/"+str(input_id)+"/pay/?cash_amount=10000",
            headers=headers)
    
    resp=client.get(BASE_URL+"/sales/"+str(input_id)+"/points",
                headers=headers)
    if exception_code == 400:
        assert resp.status_code in (exception_code, 422)
    elif exception_code!=420:
        assert resp.status_code == exception_code
    if exception_code==200:
        assert resp.json()["points"]==9