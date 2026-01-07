from typing import List
import pytest
from unittest.mock import AsyncMock, patch
from app.controllers_instances import (
    products_controller,
    sales_controller,
    sold_products_controller
)
from app.models.DAO.sale_dao import SaleDAO
from app.models.DAO.sold_product_dao import SoldProductDAO
from app.models.DTO.boolean_response_dto import BooleanResponseDTO
from app.models.DTO.product_dto import ProductTypeDTO
from app.models.DTO.sale_dto import SaleDTO
from app.models.DTO.sold_product_dto import SoldProductDTO
from app.models.errors.bad_request import BadRequestError
from app.models.errors.insufficient_stock_error import InsufficientStockError
from app.models.errors.invalid_state_error import InvalidStateError


FIRST_PRODUCT_DAO=SoldProductDAO(id=1, sale_id=2, product_barcode="0123456789111", quantity = 1,
               price_per_unit= 5.5,discount_rate=0.1)

FIRST_PRODUCT_DTO=SoldProductDTO(id=1, sale_id=2, product_barcode="0123456789111", quantity = 1,
               price_per_unit= 5.5,discount_rate=0.1)

FIFTH_PRODUCT_DAO=SoldProductDAO(id=5, sale_id=5, product_barcode="0123456789111", quantity = 1,
               price_per_unit= 105.5,discount_rate=0.0)

FIFTH_PRODUCT_DTO=SoldProductDTO(id=5, sale_id=5, product_barcode="0123456789111", quantity = 1,
               price_per_unit= 105.5,discount_rate=0.0)

SECOND_PRODUCT_DAO=SoldProductDAO(id=2, sale_id=2, product_barcode="0000000000000", quantity = 3,
               price_per_unit= 4.5,discount_rate=0.1)

SECOND_PRODUCT_DTO=SoldProductDTO(id=2, sale_id=2, product_barcode="0000000000000", quantity = 3,
               price_per_unit= 4.5,discount_rate=0.1)

THIRD_PRODUCT_DAO=SoldProductDAO(id=3, sale_id=3, product_barcode="4006381333931", quantity = 2,
               price_per_unit= 4,discount_rate=0.5)

THIRD_PRODUCT_DTO=SoldProductDTO(id=3, sale_id=3, product_barcode="4006381333931", quantity = 2,
               price_per_unit= 4,discount_rate=0.5)

NEW_SALE_DAO=SaleDAO(id=1,status="OPEN",discount_rate=0.0,lines=[],
                     created_at="2025-10-30T12:34:56Z")

NEW_SALE_DTO=SaleDTO(id=1,status="OPEN",discount_rate=0.0, 
                    created_at="2025-10-30T12:34:56Z",lines=[])

FIRST_SALE_DAO=SaleDAO(id=1,status="PENDING",discount_rate=0.0,lines=[],
                     created_at="2025-10-30T12:34:56Z",closed_at= "2025-11-30T12:34:56Z",)

FIRST_SALE_DTO=SaleDTO(id=1,status="PENDING",discount_rate=0.0, 
                    created_at="2025-10-30T12:34:56Z",closed_at= "2025-11-30T12:34:56Z",lines=[])

SECOND_SALE_DAO=SaleDAO(id=2,status="PAID",discount_rate=0.5,
                    created_at="2025-11-28T12:34:56Z", closed_at= "2025-11-30T12:34:56Z",
                    lines=[FIRST_PRODUCT_DAO,SECOND_PRODUCT_DAO])

SECOND_SALE_DTO=SaleDTO(id=2,status="PAID",discount_rate=0.5,
                    created_at="2025-11-28T12:34:56Z", closed_at= "2025-11-30T12:34:56Z",
                    lines=[FIRST_PRODUCT_DTO,SECOND_PRODUCT_DTO])

THIRD_SALE_DAO=SaleDAO(id=3,status="OPEN",discount_rate=0.1,
                     created_at="2025-10-30T12:34:56Z",lines=[THIRD_PRODUCT_DAO])

THIRD_SALE_DTO=SaleDTO(id=3,status="OPEN",discount_rate=0.1,
                     created_at="2025-10-30T12:34:56Z",lines=[THIRD_PRODUCT_DTO])

FOURTH_SALE_DAO=SaleDAO(id=4,status="PENDING",discount_rate=0.5,
                    created_at="2025-11-28T12:34:56Z", closed_at= "2025-11-30T12:34:56Z",
                    lines=[FIRST_PRODUCT_DAO,SECOND_PRODUCT_DAO])

FOURTH_SALE_DTO=SaleDTO(id=4,status="PENDING",discount_rate=0.5,
                    created_at="2025-11-28T12:34:56Z", closed_at= "2025-11-30T12:34:56Z",
                    lines=[FIRST_PRODUCT_DTO,SECOND_PRODUCT_DTO])
FIFTH_SALE_DAO=SaleDAO(id=5,status="PAID",discount_rate=0.0,
                    created_at="2025-11-28T12:34:56Z", closed_at= "2025-11-30T12:34:56Z",
                    lines=[FIFTH_PRODUCT_DAO,SECOND_PRODUCT_DAO])

FIFTH_SALE_DTO=SaleDTO(id=5,status="PAID",discount_rate=0.0,
                    created_at="2025-11-28T12:34:56Z", closed_at= "2025-11-30T12:34:56Z",
                    lines=[FIFTH_PRODUCT_DTO,SECOND_PRODUCT_DTO])

SECOND_PRODUCT_TYPE_DTO=ProductTypeDTO(id= 2,str = "hello world",
    barcode = "0000000000000",price_per_unit= 4.5,note= "None",
    quantity= 10,position= "1-A-2"
)
LIST_OF_SALE_DTO=[NEW_SALE_DTO,SECOND_SALE_DTO,THIRD_SALE_DTO]

BOOLEAN_RESPONSE_TRUE_DTO=BooleanResponseDTO(success=True)

BOOLEAN_RESPONSE_FALSE_DTO=BooleanResponseDTO(success=False)

controller=sales_controller
patch_controller="app.controllers.sale_controller"

@pytest.mark.asyncio
async def test_create_sale_controller_ok():
    controller.repo.create_sale = AsyncMock(return_value=NEW_SALE_DAO)
    result= await controller.create_sale()
    controller.repo.create_sale.assert_awaited_once()
    assert isinstance(result, SaleDTO)
    assert result.id==NEW_SALE_DTO.id
    assert result.status==NEW_SALE_DTO.status
    assert result.lines!=None

@pytest.mark.asyncio
async def test_get_all_sale_controller_ok():#control
    controller.repo.list_sales=AsyncMock(return_value=[])
    result=await controller.list_sales()
    assert isinstance(result,List)
    controller.repo.list_sales=AsyncMock(
        return_value=[NEW_SALE_DAO,SECOND_SALE_DAO,THIRD_SALE_DAO])
    result=await controller.list_sales()
    for r,l in zip(result,LIST_OF_SALE_DTO):
        assert isinstance(r, SaleDTO)
        assert r.id==l.id
        assert r.status==l.status
        assert r.closed_at==l.closed_at
        assert r.created_at==l.created_at
        for rl,ll in zip(r.lines,l.lines):
            assert rl.id==ll.id
            assert rl.sale_id==ll.sale_id
            assert rl.product_barcode==ll.product_barcode
            assert rl.quantity==ll.quantity
            assert rl.price_per_unit==ll.price_per_unit
            assert rl.discount_rate==ll.discount_rate

@pytest.mark.asyncio
async def test_get_sale_controller_ok():
    id=2
    controller.repo.get_sale_by_id=AsyncMock(
        return_value=SECOND_SALE_DAO)
    result=await controller.get_sale_by_id(id)
    assert isinstance(result, SaleDTO)
    assert result.id==SECOND_SALE_DTO.id
    assert result.status==SECOND_SALE_DTO.status
    assert result.closed_at==SECOND_SALE_DTO.closed_at
    assert result.created_at==SECOND_SALE_DTO.created_at
    for rl,ll in zip(result.lines,SECOND_SALE_DTO.lines):
        assert rl.id==ll.id
        assert rl.sale_id==ll.sale_id
        assert rl.product_barcode==ll.product_barcode
        assert rl.quantity==ll.quantity
        assert rl.price_per_unit==ll.price_per_unit
        assert rl.discount_rate==ll.discount_rate

async def test_get_sale_controller_invalid_input():
    invalid=-9
    controller.repo.get_sale_by_id=AsyncMock(
        return_value=None)
    with pytest.raises(BadRequestError) as exc_info:
        await controller.get_sale_by_id(invalid)
    assert exc_info.value.status==400

@pytest.mark.asyncio
async def test_delete_sale_controller_ok():
    id=2
    controller.repo.get_sale_by_id=AsyncMock(
        return_value=NEW_SALE_DAO)
    controller.repo.delete_sale=AsyncMock(return_value=BOOLEAN_RESPONSE_TRUE_DTO)
    result=await controller.delete_sale(id,sold_products_controller=sold_products_controller,products_controller=products_controller)
    assert result is None
    controller.repo.get_sale_by_id=AsyncMock(return_value=THIRD_SALE_DAO)
    sold_products_controller.edit_sold_product_quantity=AsyncMock(return_value=BOOLEAN_RESPONSE_TRUE_DTO)
    result=await controller.delete_sale(id,sold_products_controller=sold_products_controller,products_controller=products_controller)
    assert result is None 

@pytest.mark.asyncio
async def test_delete_sale_controller_invalid_input():
    invalid=-9
    controller.repo.get_sale_by_id=AsyncMock(
        return_value=None)
    with pytest.raises(BadRequestError) as exc_info:
        await controller.delete_sale(invalid,sold_products_controller=sold_products_controller,products_controller=products_controller)
    assert exc_info.value.status==400

@pytest.mark.asyncio
async def test_delete_sale_controller_invalid_status():
    id=2
    controller.repo.get_sale_by_id=AsyncMock(
        return_value=SECOND_SALE_DAO)
    with pytest.raises(InvalidStateError) as exc_info:
        await controller.delete_sale(id,sold_products_controller=sold_products_controller,products_controller=products_controller)
    assert exc_info.value.status==420


@pytest.mark.asyncio
async def test_add_product_ok():
    sale_id=1
    barcode="000000000000"
    amount=5

    controller.repo.get_sale_by_id=AsyncMock(
        return_value=NEW_SALE_DAO)
    products_controller.get_product_by_barcode=AsyncMock(
        return_value=SECOND_PRODUCT_TYPE_DTO)
    sold_products_controller.create_sold_product=AsyncMock(
        return_value=SECOND_PRODUCT_DTO)
    result=await controller.attach_product(sale_id,barcode,amount, products_controller=products_controller,
        sold_products_controller=sold_products_controller)
    assert result.success

@pytest.mark.asyncio
async def test_add_product_controller_invalid_input():
    invalid=9
    barcode="0000000000000"
    amount=1

    invalid=-9
    with pytest.raises(BadRequestError) as exc_info:
        await controller.attach_product(invalid,barcode,amount, products_controller=products_controller,
        sold_products_controller=sold_products_controller)
    assert exc_info.value.status==400
    id=1

    barcode=""
    with pytest.raises(BadRequestError) as exc_info:
        await controller.attach_product(id,barcode,amount, products_controller=products_controller,
        sold_products_controller=sold_products_controller)
    assert exc_info.value.status==400

    barcode="000"
    with pytest.raises(BadRequestError) as exc_info:
        await controller.attach_product(id,barcode,amount, products_controller=products_controller,
        sold_products_controller=sold_products_controller)
    assert exc_info.value.status==400
    barcode="000000000000"
    
    amount=-15
    with pytest.raises(BadRequestError) as exc_info:
        await controller.attach_product(id,barcode,amount, products_controller=products_controller,
        sold_products_controller=sold_products_controller)
    assert exc_info.value.status==400
    amount=9

    products_controller.get_product_by_barcode=AsyncMock(
        return_value=SECOND_PRODUCT_TYPE_DTO)
    controller.repo.get_sale_by_id=AsyncMock(
        return_value=NEW_SALE_DAO)
    amount=5100

    with pytest.raises(InsufficientStockError) as exc_info:
        await controller.attach_product(id,barcode,amount, products_controller=products_controller,
        sold_products_controller=sold_products_controller)
    assert exc_info.value.status==400


@pytest.mark.asyncio
async def test_add_product_controller_invalid_status():
    sale_id=1
    barcode="000000000000"
    amount=5
    controller.repo.get_sale_by_id=AsyncMock(
        return_value=SECOND_SALE_DAO)
    with pytest.raises(InvalidStateError) as exc_info:
        await controller.attach_product(sale_id,barcode,amount, products_controller=products_controller,
        sold_products_controller=sold_products_controller)
    assert exc_info.value.status==420
    sale_id=2
    controller.repo.get_sale_by_id=AsyncMock(
        return_value=FOURTH_SALE_DTO)
    with pytest.raises(InvalidStateError) as exc_info:
        await controller.attach_product(sale_id,barcode,amount, products_controller=products_controller,
        sold_products_controller=sold_products_controller)
    assert exc_info.value.status==420


@pytest.mark.asyncio
async def test_edit_product_controller_ok():
    sale_id=3
    barcode="4006381333931"
    amount=5

    controller.repo.get_sale_by_id=AsyncMock(
        return_value=THIRD_SALE_DTO)
    sold_products_controller.edit_sold_product_quantity=AsyncMock(
        return_value=BOOLEAN_RESPONSE_TRUE_DTO)
    result=await controller.edit_sold_product_quantity(sale_id, barcode, 
        amount, sold_products_controller=sold_products_controller,products_controller=products_controller)

    assert result.success

@pytest.mark.asyncio
async def test_edit_product_controller_invalid_input():
    invalid=-9
    barcode=""
    amount=-1
    with pytest.raises(BadRequestError) as exc_info:
        await controller.edit_sold_product_quantity(invalid, barcode, 
        amount, sold_products_controller=sold_products_controller,products_controller=products_controller)

    assert exc_info.value.status==400

    id=3
    controller.repo.get_sale_by_id=AsyncMock(
        return_value=THIRD_SALE_DTO)
    with pytest.raises(BadRequestError) as exc_info:
        await controller.edit_sold_product_quantity(id, barcode, 
        amount, sold_products_controller=sold_products_controller,products_controller=products_controller)
    assert exc_info.value.status==400

    barcode="000"
    with pytest.raises(BadRequestError) as exc_info:
        await controller.edit_sold_product_quantity(id, barcode, 
        amount, sold_products_controller=sold_products_controller,products_controller=products_controller)
    assert exc_info.value.status==400

    barcode="000000000001"
    controller.repo.get_sale_by_id=AsyncMock(
        return_value=THIRD_SALE_DTO)
    sold_products_controller.edit_sold_product_quantity=AsyncMock(
        return_value=BOOLEAN_RESPONSE_FALSE_DTO)
    amount=5100
    with pytest.raises(BadRequestError) as exc_info:
        await controller.edit_sold_product_quantity(id, barcode, 
        amount, sold_products_controller=sold_products_controller,products_controller=products_controller)
    assert exc_info.value.status==400

@pytest.mark.asyncio
async def test_edit_product_controller_invalid_status():
    sale_id=2
    barcode="4006381333931"
    amount=5
    controller.repo.get_sale_by_id=AsyncMock(
        return_value=SECOND_SALE_DAO)
    with pytest.raises(InvalidStateError) as exc_info:
        await controller.edit_sold_product_quantity(sale_id, barcode, 
        amount, sold_products_controller=sold_products_controller,products_controller=products_controller) 
    assert exc_info.value.status==420

@pytest.mark.asyncio
async def test_edit_sale_discount_controller_ok():
    sale_id=1
    discount_rate=0.26

    controller.repo.edit_sale_discount=AsyncMock(result_value=BOOLEAN_RESPONSE_TRUE_DTO)
    result=await controller.edit_sale_discount(sale_id,discount_rate)
    assert result.success

@pytest.mark.asyncio
async def test_edit_sale_discount_controller_invalid_input():
    sale_id=1
    discount_rate=0.1

    sale_id=-5
    with pytest.raises(BadRequestError) as exc_info:
        await controller.edit_sale_discount(sale_id,discount_rate)
    assert exc_info.value.status==400
    sale_id=1

    discount_rate=5
    with pytest.raises(BadRequestError) as exc_info:
        await controller.edit_sale_discount(sale_id,discount_rate)
    assert exc_info.value.status==400

    discount_rate=-0.2
    with pytest.raises(BadRequestError) as exc_info:
        await controller.edit_sale_discount(sale_id,discount_rate)
    assert exc_info.value.status==400


@pytest.mark.asyncio
async def test_edit_product_discount_controller_ok():
    sale_id=1
    discount_rate=0.26
    barcode="4006381333931"
    controller.repo.get_sale_by_id=AsyncMock(
        return_value=THIRD_SALE_DTO)
    sold_products_controller.edit_sold_product_discount=AsyncMock(
        return_value=BOOLEAN_RESPONSE_TRUE_DTO)
    controller.repo.edit_product_discount=AsyncMock(result_value=BOOLEAN_RESPONSE_TRUE_DTO)
    result=await controller.edit_product_discount(sale_id,barcode,discount_rate,sold_products_controller)
    assert result.success

@pytest.mark.asyncio
async def test_edit_product_discount_controller_invalid_input():
    sale_id=1
    discount_rate=0.26
    barcode="0000000000000"

    sale_id=-1
    with pytest.raises(BadRequestError) as exc_info:
        await controller.edit_product_discount(sale_id,barcode,discount_rate,sold_products_controller)
    assert exc_info.value.status==400
    sale_id=1

    barcode=""
    with pytest.raises(BadRequestError) as exc_info:
        await controller.edit_product_discount(sale_id,barcode,discount_rate,sold_products_controller)
    assert exc_info.value.status==400

    barcode="004"
    with pytest.raises(BadRequestError) as exc_info:
        await controller.edit_product_discount(sale_id,barcode,discount_rate,sold_products_controller)
    assert exc_info.value.status==400
    barcode="4006381333931"

    discount_rate=-0.2
    with pytest.raises(BadRequestError) as exc_info:
        await controller.edit_product_discount(sale_id,barcode,discount_rate,sold_products_controller)
    assert exc_info.value.status==400

    discount_rate=1.2
    with pytest.raises(BadRequestError) as exc_info:
        await controller.edit_product_discount(sale_id,barcode,discount_rate,sold_products_controller)
    assert exc_info.value.status==400
    
@pytest.mark.asyncio
async def test_edit_product_controller_invalid_status():
    sale_id=2
    barcode="4006381333931"
    discount_rate=0.5
    controller.repo.get_sale_by_id=AsyncMock(
        return_value=SECOND_SALE_DAO)
    
    with pytest.raises(InvalidStateError) as exc_info:
        await controller.edit_product_discount(sale_id,barcode,discount_rate,sold_products_controller)
    assert exc_info.value.status==420

    controller.repo.get_sale_by_id=AsyncMock(
        return_value=FOURTH_SALE_DTO)
    
    with pytest.raises(InvalidStateError) as exc_info:
        await controller.edit_product_discount(sale_id,barcode,discount_rate,sold_products_controller)
    assert exc_info.value.status==420

@pytest.mark.asyncio
async def test_close_sale_controller_ok():
    sale_id=3
    controller.repo.get_sale_by_id=AsyncMock(
        return_value=THIRD_SALE_DTO)
    controller.repo.edit_sale_status=AsyncMock(return_value=BOOLEAN_RESPONSE_TRUE_DTO)
    result=await controller.close_sale(sale_id,products_controller=products_controller,sold_products_controller=sold_products_controller)
    assert result.success

@pytest.mark.asyncio 
async def test_close_sale_controller_invalid_input():
    sale_id=-15
    with pytest.raises(BadRequestError) as exc_info:
        await controller.close_sale(sale_id,products_controller=products_controller,sold_products_controller=sold_products_controller)

    assert exc_info.value.status==400

@pytest.mark.asyncio
async def test_close_sale_controller_invalid_status():
    sale_id=2
    controller.repo.get_sale_by_id=AsyncMock(
        return_value=SECOND_SALE_DAO)
    
    with pytest.raises(InvalidStateError) as exc_info:
        await controller.close_sale(sale_id,products_controller=products_controller,sold_products_controller=sold_products_controller)
    assert exc_info.value.status==420

    controller.repo.get_sale_by_id=AsyncMock(
        return_value=FOURTH_SALE_DTO)
    
    with pytest.raises(InvalidStateError) as exc_info:
        await controller.close_sale(sale_id,products_controller=products_controller,sold_products_controller=sold_products_controller)
    assert exc_info.value.status==420

@pytest.mark.asyncio
async def test_paid_sale_controller_ok():
    sale_id=4
    cash_amount=200
    controller.repo.get_sale_by_id=AsyncMock(
        return_value=FOURTH_SALE_DTO)
    controller.repo.edit_sale_status=AsyncMock(return_value=BOOLEAN_RESPONSE_TRUE_DTO)
    result=await controller.pay_sale(sale_id,cash_amount)
    assert result.change==191.45

    controller.repo.get_sale_by_id=AsyncMock(
        return_value=FIRST_SALE_DTO)
    controller.repo.edit_sale_status=AsyncMock(return_value=BOOLEAN_RESPONSE_TRUE_DTO)
    result=await controller.pay_sale(sale_id,cash_amount)
    assert result.change==cash_amount

@pytest.mark.asyncio 
async def test_paid_sale_controller_invalid_input():
    sale_id=15
    cash_amount=200

    sale_id=-5
    with pytest.raises(BadRequestError) as exc_info:
        await controller.pay_sale(sale_id,cash_amount)
    assert exc_info.value.status==400
    sale_id=4

    cash_amount=-9
    with pytest.raises(BadRequestError) as exc_info:
        await controller.pay_sale(sale_id,cash_amount)
    assert exc_info.value.status==400

    controller.repo.get_sale_by_id=AsyncMock(
        return_value=FOURTH_SALE_DTO)
    controller.repo.edit_sale_status=AsyncMock(return_value=BOOLEAN_RESPONSE_TRUE_DTO)
    cash_amount=2
    with pytest.raises(BadRequestError) as exc_info:
        await controller.pay_sale(sale_id,cash_amount)
    assert exc_info.value.status==400

@pytest.mark.asyncio
async def test_paid_sale_controller_invalid_status():
    sale_id=2
    cash_amount=200
    controller.repo.get_sale_by_id=AsyncMock(
        return_value=NEW_SALE_DTO)
    
    with pytest.raises(InvalidStateError) as exc_info:
        await controller.pay_sale(sale_id,cash_amount)
    assert exc_info.value.status==420

    controller.repo.get_sale_by_id=AsyncMock(
        return_value=SECOND_SALE_DTO)
    
    with pytest.raises(InvalidStateError) as exc_info:
        await controller.pay_sale(sale_id,cash_amount)
    assert exc_info.value.status==420

@pytest.mark.asyncio 
async def test_get_point_controller_ok():
    sale_id=2
    controller.repo.get_sale_by_id=AsyncMock(
        return_value=FIFTH_SALE_DTO)
    result=await controller.get_points(sale_id)
    assert result.points==11

@pytest.mark.asyncio
async def test_get_point_controller_invalid_input():
    
    sale_id=-5
    controller.repo.get_sale_by_id=AsyncMock(
        return_value=FIFTH_SALE_DTO)
    
    with pytest.raises(BadRequestError) as exc_info:
        await controller.get_points(sale_id)
    assert exc_info.value.status==400

@pytest.mark.asyncio
async def test_get_point_controller_invalid_status():
    sale_id=2
    controller.repo.get_sale_by_id=AsyncMock(
        return_value=NEW_SALE_DTO)
    
    with pytest.raises(InvalidStateError) as exc_info:
        await controller.get_points(sale_id)
    assert exc_info.value.status==420

    controller.repo.get_sale_by_id=AsyncMock(
        return_value=FOURTH_SALE_DTO)
    
    with pytest.raises(InvalidStateError) as exc_info:
        await controller.get_points(sale_id)
    assert exc_info.value.status==420