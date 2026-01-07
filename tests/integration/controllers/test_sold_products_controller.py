import pytest
from unittest.mock import AsyncMock, patch
from app.controllers_instances import sold_products_controller
from app.models.DAO.sold_product_dao import SoldProductDAO
from app.models.DTO.boolean_response_dto import BooleanResponseDTO
from app.models.DTO.sold_product_dto import SoldProductDTO
from app.models.errors.bad_request import BadRequestError
from app.models.errors.notfound_error import NotFoundError

NEW_PRODUCT_DAO=SoldProductDAO(id=6, sale_id=1, product_barcode="0123456789111", quantity = 1,
               price_per_unit= 5.5,discount_rate=0.0)

NEW_PRODUCT_DTO=SoldProductDTO(id=6, sale_id=1, product_barcode="0123456789111", quantity = 1,
               price_per_unit= 5.5,discount_rate=0.0)

FIRST_PRODUCT_DAO=SoldProductDAO(id=1, sale_id=2, product_barcode="0123456789111", quantity = 1,
               price_per_unit= 5.5,discount_rate=0.1)

FIRST_PRODUCT_DTO=SoldProductDTO(id=1, sale_id=2, product_barcode="0123456789111", quantity = 1,
               price_per_unit= 5.5,discount_rate=0.1)

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

BOOLEAN_RESPONSE_TRUE_DTO=BooleanResponseDTO(success=True)

BOOLEAN_RESPONSE_FALSE_DTO=BooleanResponseDTO(success=False)

controller=sold_products_controller
patch_controller="app.controllers.sold_products_controller"

@pytest.mark.asyncio
async def test_create_sold_product_controller_ok():
    controller.repo.create_sold_product=AsyncMock(return_value=NEW_PRODUCT_DAO)
    result=await controller.create_sold_product(NEW_PRODUCT_DAO.id,
        NEW_PRODUCT_DAO.sale_id,
        NEW_PRODUCT_DAO.product_barcode,
        NEW_PRODUCT_DAO.quantity, 
        NEW_PRODUCT_DAO.price_per_unit)
    assert isinstance(result,SoldProductDTO)
    assert result.id==NEW_PRODUCT_DTO.id
    assert result.sale_id==NEW_PRODUCT_DTO.sale_id
    assert result.product_barcode==NEW_PRODUCT_DTO.product_barcode
    assert result.quantity==NEW_PRODUCT_DTO.quantity
    assert result.price_per_unit==NEW_PRODUCT_DTO.price_per_unit
    assert result.discount_rate==0.0

@pytest.mark.asyncio
async def test_create_sold_product_controller_invalid_input():
    id=8
    sale_id=id
    quantity=9
    barcode="0000000000000"
    price_unit=8
    
    id=-8
    with pytest.raises(BadRequestError) as exc_info:
        await controller.create_sold_product(id,sale_id,barcode,quantity, 
        price_unit)
    assert exc_info.value.status==400
    id=10

    sale_id=-8
    with pytest.raises(BadRequestError) as exc_info:
        await controller.create_sold_product(id,sale_id,barcode,quantity, 
        price_unit)
    assert exc_info.value.status==400
    sale_id=id

    quantity=-9
    with pytest.raises(BadRequestError) as exc_info:
        await controller.create_sold_product(id,sale_id,barcode,quantity, 
        price_unit)
    assert exc_info.value.status==400
    quantity=9
    
    barcode=""
    with pytest.raises(BadRequestError) as exc_info:
        await controller.create_sold_product(id,sale_id,barcode,quantity, 
        price_unit)
    assert exc_info.value.status==400

    barcode="4567895552000"
    with pytest.raises(BadRequestError) as exc_info:
        await controller.create_sold_product(id,sale_id,barcode,quantity, 
        price_unit)
    assert exc_info.value.status==400
    barcode="0000000000000"
    
    price_unit=-8
    with pytest.raises(BadRequestError) as exc_info:
        await controller.create_sold_product(id,sale_id,barcode,quantity, 
        price_unit)
    assert exc_info.value.status==400
    price_unit=8

@pytest.mark.asyncio
async def test_get_sold_product_by_id_controller_ok():#control
    id=6
    controller.repo.get_sold_product_by_id=AsyncMock(return_value=[NEW_PRODUCT_DAO])
    result=await controller.get_sold_product_by_id(id)

    assert isinstance(result,SoldProductDTO)
    assert result.id==NEW_PRODUCT_DTO.id
    assert result.sale_id==NEW_PRODUCT_DTO.sale_id
    assert result.product_barcode==NEW_PRODUCT_DTO.product_barcode
    assert result.quantity==NEW_PRODUCT_DTO.quantity
    assert result.price_per_unit==NEW_PRODUCT_DTO.price_per_unit
    assert result.discount_rate==0.0

@pytest.mark.asyncio
async def test_get_sold_product_by_id_controller_invalid_input():
    id=-6
    controller.repo.get_sold_product_by_id=AsyncMock(return_value=None)
    with pytest.raises(BadRequestError) as exc_info:
        await controller.get_sold_product_by_id(id)
    assert exc_info.value.status==400

@pytest.mark.asyncio
async def test_get_sold_product_by_id_controller_not_found():
    id=6
    controller.repo.get_sold_product_by_id=AsyncMock(return_value=None)
    with pytest.raises(NotFoundError) as exc_info:
        await controller.get_sold_product_by_id(id)
    assert exc_info.value.status==404



@pytest.mark.asyncio
async def test_edit_sold_product_quantity_controller_ok():
    id=1
    sale_id=1
    quantity=3
    
    controller.repo.edit_sold_product_quantity=AsyncMock(result_value=BOOLEAN_RESPONSE_TRUE_DTO)
    result=await controller.edit_sold_product_quantity(id,sale_id,quantity)
    assert result.success

@pytest.mark.asyncio
async def test_edit_sold_product_quantity_controller_invalid_input():
    id=9
    sale_id=9
    quantity=45

    id=-9
    with pytest.raises(BadRequestError) as exc_info:
        await controller.edit_sold_product_quantity(id,sale_id,quantity)
    assert exc_info.value.status==400
    id=9
    
    sale_id=-4567895555123
    with pytest.raises(BadRequestError) as exc_info:
        await controller.edit_sold_product_quantity(id,sale_id,quantity)
    assert exc_info.value.status==400
    sale_id=9

@pytest.mark.asyncio
async def test_edit_sold_product_discount_controller_ok():
    id=1
    sale_id=1
    discount=0.5
    
    controller.repo.edit_sold_product_discount=AsyncMock(result_value=BOOLEAN_RESPONSE_TRUE_DTO)
    result=await controller.edit_sold_product_discount(id,sale_id,discount)
    assert result.success


@pytest.mark.asyncio
async def test_edit_sold_product_discount_controller_invalid_input():
    id=9
    sale_id=9
    discount=0.45

    id=-9
    with pytest.raises(BadRequestError) as exc_info:
        await controller.edit_sold_product_discount(id,sale_id,discount)
    assert exc_info.value.status==400
    id=9
    
    discount=-0.5
    with pytest.raises(BadRequestError) as exc_info:
        await controller.edit_sold_product_discount(id,sale_id,discount)
    assert exc_info.value.status==400
    
    discount=2
    with pytest.raises(BadRequestError) as exc_info:
        await controller.edit_sold_product_discount(id,sale_id,discount)
    assert exc_info.value.status==400
    discount=0.1