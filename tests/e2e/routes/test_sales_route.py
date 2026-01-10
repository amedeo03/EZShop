from fastapi.testclient import TestClient
from httpx import AsyncClient
from app.config.config import ROUTES
from main import app
from unittest.mock import patch, AsyncMock
from init_db import init_db, reset
import pytest
import asyncio


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

NEW_SALES={
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
                "id": 10,
                "status": "PAID",
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

CLOSE_SALES={
                "id": 10,
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


def test_create_sale_route_ok(client,auth_tokens):
    with patch("app.routes.sales_route.controller.create_sale",new_callable=AsyncMock) as mockCreateSale:
        mockCreateSale.return_value=NEW_SALES
        resp=client.post(BASE_URL+"/sales/",json=NEW_SALES,headers=auth_header(auth_tokens, "admin"))
        assert resp.status_code==201
        data=resp.json()
        assert data["status"] == NEW_SALES["status"]
        assert data["discount_rate"] == NEW_SALES["discount_rate"]
        assert data["status"] == NEW_SALES["status"]
        assert data["created_at"] == NEW_SALES["created_at"]
        assert data["closed_at"] == NEW_SALES["closed_at"]
        for line_s,line_l in zip(data["lines"],NEW_SALES["lines"]):
            assert line_s["id"] ==line_l["id"]
            assert line_s["sale_id"] ==line_l["sale_id"]
            assert line_s["product_barcode"] ==line_l["product_barcode"]
            assert line_s["quantity"] ==line_l["quantity"]
            assert line_s["price_per_unit"] ==line_l["price_per_unit"]
            assert line_s["discount_rate"] ==line_l["discount_rate"]

def test_create_sale_route_unauthenticated(client):
    resp=client.post(BASE_URL+"/sales/",json=NEW_SALES)
    assert resp.status_code==401

def test_get_all_sales_route_ok(client,auth_tokens):
    with patch("app.routes.sales_route.controller.list_sales",new_callable=AsyncMock) as mockAllSale:
        mockAllSale.return_value=LIST_ALL_SALES
        resp=client.get(BASE_URL+"/sales/",headers=auth_header(auth_tokens, "admin"))
        assert resp.status_code==200
        data=resp.json()
        for sale,list in zip(data,LIST_ALL_SALES):
            assert sale["status"] == list["status"]
            assert sale["discount_rate"] == list["discount_rate"]
            assert sale["status"] == list["status"]
            assert sale["created_at"] == list["created_at"]
            assert sale["closed_at"] == list["closed_at"]
            for line_s,line_l in zip(sale["lines"],list["lines"]):
                assert line_s["id"] ==line_l["id"]
                assert line_s["sale_id"] ==line_l["sale_id"]
                assert line_s["product_barcode"] ==line_l["product_barcode"]
                assert line_s["quantity"] ==line_l["quantity"]
                assert line_s["price_per_unit"] ==line_l["price_per_unit"]
                assert line_s["discount_rate"] ==line_l["discount_rate"]

def test_get_all_sales_route_unauthenticated(client):
    resp=client.get(BASE_URL+"/sales/")
    assert resp.status_code==401

def test_get_sale_id_route_ok(client,auth_tokens):
    with patch("app.routes.sales_route.controller.get_sale_by_id",new_callable=AsyncMock) as mockSale:
        mockSale.return_value=NEW_SALES
        resp=client.get(BASE_URL+"/sales/10",headers=auth_header(auth_tokens, "admin"))
        assert resp.status_code==200
        data=resp.json()
        assert data["status"] == NEW_SALES["status"]
        assert data["discount_rate"] == NEW_SALES["discount_rate"]
        assert data["status"] == NEW_SALES["status"]
        assert data["created_at"] == NEW_SALES["created_at"]
        assert data["closed_at"] == NEW_SALES["closed_at"]
        for line_s,line_l in zip(data["lines"],NEW_SALES["lines"]):
            assert line_s["id"] ==line_l["id"]
            assert line_s["sale_id"] ==line_l["sale_id"]
            assert line_s["product_barcode"] ==line_l["product_barcode"]
            assert line_s["quantity"] ==line_l["quantity"]
            assert line_s["price_per_unit"] ==line_l["price_per_unit"]
            assert line_s["discount_rate"] ==line_l["discount_rate"]

def test_get_sale_id_route_invalid_id(client,auth_tokens):
    invalid={"a","-4"}
    for i in invalid:  
        resp=client.get(BASE_URL+"/sales/"+i,headers=auth_header(auth_tokens, "admin"))
        assert resp.status_code in (400,422)

def test_get_sale_id_route_unauthenticated(client):
    resp=client.get(BASE_URL+"/sales/10")
    assert resp.status_code==401

def test_get_sale_id_route_not_found(client,auth_tokens):
    resp = client.get(BASE_URL + "/sales/111", headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code == 404

def test_delete_sale_route_ok(client,auth_tokens):
    with patch("app.routes.sales_route.controller.create_sale",new_callable=AsyncMock) as mockCreateSale:
        mockCreateSale.return_value=PAID_SALE
        client.post(BASE_URL+"/sales/",json=PAID_SALE,headers=auth_header(auth_tokens, "admin"))
    with patch("app.routes.sales_route.controller.delete_sale",new_callable=AsyncMock) as mockDeleteSale:
        mockDeleteSale.return_value={}
        resp=client.delete(BASE_URL+"/sales/10",headers=auth_header(auth_tokens, "admin"))
        assert resp.status_code==204

def test_delete_sale_route_invalid_id(client,auth_tokens):
    invalid={"a","-4"}
    for i in invalid:  
        resp=client.get(BASE_URL+"/sales/"+i,headers=auth_header(auth_tokens, "admin"))
        assert resp.status_code in (400,422)

def test_product_added_route_ok(client,auth_tokens):
    query="?barcode=0123456789&amount=5"
    with patch("app.routes.sales_route.controller.attach_product",new_callable=AsyncMock) as mockAddItem:
        mockAddItem.return_value=BOOLEAN_RESPONSE
        resp = client.post(BASE_URL + "/sales/10"+"/items"+query, headers=auth_header(auth_tokens, "admin"))
        assert resp.status_code == 201
        data=resp.json()
        assert data["success"]

def test_product_added_route_invalid_input(client,auth_tokens):
    query="?barcode=&amount=5"
    resp = client.post(BASE_URL + "/sales/10"+"/items"+query, headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code == 400

def test_product_added_route_unauthenticated(client):
    query="?barcode=0123456789&amount=5"
    resp = client.post(BASE_URL + "/sales/10"+"/items"+query)
    assert resp.status_code == 401

def test_product_added_route_not_found(client,auth_tokens):
    resp = client.get(BASE_URL + "/sales/10", headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code == 404
    

def test_remove_product_route_ok(client,auth_tokens):
    query="?barcode=0123456789&amount=5"
    with patch("app.routes.sales_route.controller.create_sale",new_callable=AsyncMock) as mockCreateSale:
        mockCreateSale.return_value=NEW_SALES
        client.post(BASE_URL+"/sales/",json=NEW_SALES,headers=auth_header(auth_tokens, "admin"))
    with patch("app.routes.sales_route.controller.edit_sold_product_quantity",new_callable=AsyncMock) as mockAddItem:
        mockAddItem.return_value=BOOLEAN_RESPONSE
        resp = client.delete(BASE_URL + "/sales/10"+"/items"+query, headers=auth_header(auth_tokens, "admin"))
        assert resp.status_code == 202
        data=resp.json()
        assert data["success"]

def test_remove_product_route_invalid_input(client,auth_tokens):
    query="?barcode=&amount=5"
    invalid={"a","-4"}
    with patch("app.routes.sales_route.controller.create_sale",new_callable=AsyncMock) as mockCreateSale:
       mockCreateSale.return_value=NEW_SALES
       client.post(BASE_URL+"/sales/",json=NEW_SALES,headers=auth_header(auth_tokens, "admin"))
    resp = client.delete(BASE_URL + "/sales/10"+"/items"+query, headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code in (400,404)
    query="?barcode=0000000000&amount=5"
    for i in invalid:
        resp = client.delete(BASE_URL + "/sales/"+i+"/items"+query, headers=auth_header(auth_tokens, "admin"))
        assert resp.status_code in (400,422)
def test_remove_product_route_unauthenticated(client):
    query="?barcode=0123456789&amount=5"
    resp = client.delete(BASE_URL + "/sales/10"+"/items"+query)
    assert resp.status_code == 401

def test_remove_product_route_not_found(client,auth_tokens):
    query="?barcode=0123456789&amount=5"
    resp = client.delete(BASE_URL + "/sales/10/items"+query, headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code in (404,400)

def test_set_discount_route_ok(client,auth_tokens):
    query="?discount_rate=0.04"
    with patch("app.routes.sales_route.controller.create_sale",new_callable=AsyncMock) as mockCreateSale:
        mockCreateSale.return_value=NEW_SALES
        client.post(BASE_URL+"/sales/",json=NEW_SALES,headers=auth_header(auth_tokens, "admin"))
    with patch("app.routes.sales_route.controller.edit_sale_discount",new_callable=AsyncMock) as mockSetDiscount:
        mockSetDiscount.return_value=BOOLEAN_RESPONSE
        resp=client.patch(BASE_URL+"/sales/10/discount"+query,json=NEW_SALES,headers=auth_header(auth_tokens, "admin"))
        assert resp.status_code==200
        assert resp.json()["success"]

def test_set_discount_route_invalid_input(client,auth_tokens):
    invalid={"a","-4"}
    query="?discount_rate=w"
    with patch("app.routes.sales_route.controller.create_sale",new_callable=AsyncMock) as mockCreateSale:
        mockCreateSale.return_value=NEW_SALES
        client.post(BASE_URL+"/sales/",json=NEW_SALES,headers=auth_header(auth_tokens, "admin"))
    resp=client.patch(BASE_URL+"/salses/10/discount"+query,headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code in (400,404)
    query="?discount_rate=0.5"
    for i in invalid:  
        resp=client.patch(BASE_URL+"/sales/"+i+"/discount"+query,headers=auth_header(auth_tokens, "admin"))
        assert resp.status_code in (400,422)

def test_set_discount_route_unauthenticated(client):
    query="?discount_rate=0.5"
    resp = client.patch(BASE_URL + "/sales/10"+"/discount"+query)
    assert resp.status_code == 401

def test_set_discount_route_not_found(client,auth_tokens):
    query="?discount_rate=0.5"
    resp = client.patch(BASE_URL + "/sales/10"+"/discount"+query, headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code == 404

def test_set_discount_product_route_ok(client,auth_tokens):
    query="?discount_rate=0.04"
    with patch("app.routes.sales_route.controller.create_sale",new_callable=AsyncMock) as mockCreateSale:
        mockCreateSale.return_value=NEW_SALES
        client.post(BASE_URL+"/sales/",json=NEW_SALES,headers=auth_header(auth_tokens, "admin"))
    with patch("app.routes.sales_route.controller.edit_product_discount",new_callable=AsyncMock) as mockSetDiscount:
        mockSetDiscount.return_value=BOOLEAN_RESPONSE
        resp=client.patch(BASE_URL+"/sales/10/items/0123456789/discount"+query,json=NEW_SALES,headers=auth_header(auth_tokens, "admin"))
        assert resp.status_code==200
        assert resp.json()["success"]

def test_set_discount_product_route_invalid_input(client,auth_tokens):
    invalid={"a","-4"}
    query="?discount_rate=w"
    with patch("app.routes.sales_route.controller.create_sale",new_callable=AsyncMock) as mockCreateSale:
        mockCreateSale.return_value=NEW_SALES
        client.post(BASE_URL+"/sales/",json=NEW_SALES,headers=auth_header(auth_tokens, "admin"))
    resp=client.patch(BASE_URL+"/sales/10/items/0123456789/discount"+query,headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code in (400,404,422)
    query="?discount_rate=0.5"
    for i in invalid:  
        resp=client.patch(BASE_URL+"/sales/"+i+"/items/0123456789/discount"+query,headers=auth_header(auth_tokens, "admin"))
        assert resp.status_code in (400,422)
    for i in invalid:  
        resp=client.patch(BASE_URL+"/sales/10/items/"+i+"/discount"+query,headers=auth_header(auth_tokens, "admin"))
        assert resp.status_code in (400,422)

def test_set_discount_product_route_unauthenticated(client):
    query="?discount_rate=0.5"
    resp = client.patch(BASE_URL + "/sales/10/items/0123456789/discount"+query)
    assert resp.status_code == 401

def test_set_discount_product_route_not_found(client,auth_tokens):
    query="?discount_rate=0.5"
    resp = client.patch(BASE_URL + "/sales/10/item/0123456789"+"/discount"+query, headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code == 404

def test_close_sale_route_ok(client,auth_tokens):
    with patch("app.routes.sales_route.controller.create_sale",new_callable=AsyncMock) as mockCreateSale:
        mockCreateSale.return_value=NEW_SALES
        client.post(BASE_URL+"/sales/",json=NEW_SALES,headers=auth_header(auth_tokens, "admin"))
    with patch("app.routes.sales_route.controller.close_sale",new_callable=AsyncMock) as mockSetDiscount:
        mockSetDiscount.return_value=BOOLEAN_RESPONSE
        resp=client.patch(BASE_URL+"/sales/10/close",headers=auth_header(auth_tokens, "admin"))
        assert resp.status_code==200
        assert resp.json()["success"]

def test_close_sale_route_invalid_input(client,auth_tokens):
    invalid={"a","-4"}
    with patch("app.routes.sales_route.controller.create_sale",new_callable=AsyncMock) as mockCreateSale:
        mockCreateSale.return_value=NEW_SALES
        client.post(BASE_URL+"/sales/",json=NEW_SALES,headers=auth_header(auth_tokens, "admin"))
    for i in invalid:  
        resp=client.patch(BASE_URL+"/sales/"+i+"/close",headers=auth_header(auth_tokens, "admin"))
        assert resp.status_code in (400,422)

def test_close_sale_route_unauthenticated(client):
    resp = client.patch(BASE_URL + "/sales/10"+"/close")
    assert resp.status_code == 401

def test_close_sale_route_not_found(client,auth_tokens):
    resp = client.patch(BASE_URL + "/sales/10"+"/close", headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code == 404

def test_paid_sale_route_ok(client,auth_tokens):
    query="?cash_amount=5"
    with patch("app.routes.sales_route.controller.create_sale",new_callable=AsyncMock) as mockCreateSale:
        mockCreateSale.return_value=CLOSE_SALES
        client.post(BASE_URL+"/sales/",json=CLOSE_SALES,headers=auth_header(auth_tokens, "admin"))
    with patch("app.routes.sales_route.controller.pay_sale",new_callable=AsyncMock) as mockSetDiscount:
        mockSetDiscount.return_value=CHANGE_RESPONSE
        resp=client.patch(BASE_URL+"/sales/10/pay"+query,headers=auth_header(auth_tokens, "admin"))
        assert resp.status_code==200
        assert resp.json()["change"]==5

def test_paid_sale_route_invalid_input(client,auth_tokens):
    invalid={"a","-4"}
    query="?cash_amount=a"
    with patch("app.routes.sales_route.controller.create_sale",new_callable=AsyncMock) as mockCreateSale:
        mockCreateSale.return_value=CLOSE_SALES
        client.post(BASE_URL+"/sales/",json=CLOSE_SALES,headers=auth_header(auth_tokens, "admin"))
    resp=client.patch(BASE_URL+"/sales/10/pay"+query,headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code in (400,422)
    query="?cash_amount=5"
    for i in invalid:  
        resp=client.patch(BASE_URL+"/sales/"+i+"/pay",headers=auth_header(auth_tokens, "admin"))
        assert resp.status_code in (400,422)

def test_paid_sale_route_unauthenticated(client):
    query="?cash_amount=5"
    resp = client.patch(BASE_URL + "/sales/10"+"/pay"+query)
    assert resp.status_code == 401

def test_paid_sale_route_not_found(client,auth_tokens):
    query="?cash_amount=5"
    resp = client.patch(BASE_URL + "/sales/10"+"/pay"+query, headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code == 404

def test_points_route_ok(client,auth_tokens):
    with patch("app.routes.sales_route.controller.create_sale",new_callable=AsyncMock) as mockCreateSale:
        mockCreateSale.return_value=CLOSE_SALES
        client.post(BASE_URL+"/sales/",json=CLOSE_SALES,headers=auth_header(auth_tokens, "admin"))
    with patch("app.routes.sales_route.controller.get_points",new_callable=AsyncMock) as mockSetDiscount:
        mockSetDiscount.return_value=POINT_RESPONSE
        resp=client.get(BASE_URL+"/sales/10/points",headers=auth_header(auth_tokens, "admin"))
        assert resp.status_code==200
        assert resp.json()["points"]==15

def test_points_route_invalid_input(client,auth_tokens):
    invalid={"a","-4"}
    with patch("app.routes.sales_route.controller.create_sale",new_callable=AsyncMock) as mockCreateSale:
        mockCreateSale.return_value=NEW_SALES
        client.post(BASE_URL+"/sales/",json=NEW_SALES,headers=auth_header(auth_tokens, "admin"))
    for i in invalid:  
        resp=client.get(BASE_URL+"/sales/"+i+"/points",headers=auth_header(auth_tokens, "admin"))
        assert resp.status_code in (400,422)
    
def test_points_route_unauthenticated(client):
    resp = client.get(BASE_URL + "/sales/10"+"/points")
    assert resp.status_code == 401

def test_points_route_not_found(client,auth_tokens):
    resp = client.get(BASE_URL + "/sales/10"+"/points", headers=auth_header(auth_tokens, "admin"))
    assert resp.status_code == 404