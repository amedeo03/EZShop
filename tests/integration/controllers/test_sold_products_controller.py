from typing import List
import pytest
from datetime import datetime, timezone
import pytest_asyncio
from sqlalchemy import select
from app.controllers.products_controller import ProductsController
from app.controllers.sales_controller import SalesController
from app.controllers.sold_products_controller import SoldProductsController
from app.controllers_instances import (
    products_controller,
    sold_products_controller
)
from app.database.database import Base
from app.models.DAO.product_dao import ProductDAO
from app.models.DAO.sale_dao import SaleDAO
from app.models.DAO.sold_product_dao import SoldProductDAO
from app.models.DTO.boolean_response_dto import BooleanResponseDTO
from app.models.DTO.product_dto import ProductTypeDTO
from app.models.DTO.sale_dto import SaleDTO
from app.models.DTO.sold_product_dto import SoldProductDTO
from app.models.errors.bad_request import BadRequestError
from app.models.errors.insufficient_stock_error import InsufficientStockError
from app.models.errors.invalid_state_error import InvalidStateError
from app.models.errors.notfound_error import NotFoundError
from app.repositories.products_repository import ProductsRepository
from app.repositories.sales_repository import SalesRepository
from app.repositories.sold_products_repository import SoldProductsRepository
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

START_TEST=datetime.now(timezone.utc).replace(  # type: ignore
                    microsecond=0
                )
FIRST_PRODUCT_DAO=SoldProductDAO(id=1, sale_id=2, product_barcode="0123456789111", quantity = 1,
               price_per_unit= 5.5,discount_rate=0.1)

FIRST_PRODUCT_DTO=SoldProductDTO(id=1, sale_id=2, product_barcode="0123456789111", quantity = 1,
               price_per_unit= 5.5,discount_rate=0.1)

FIFTH_PRODUCT_DAO=SoldProductDAO(id=5, sale_id=5, product_barcode="4006381333932", quantity = 1,
               price_per_unit= 105.5,discount_rate=0.0)

FIFTH_PRODUCT_DTO=SoldProductDTO(id=5, sale_id=5, product_barcode="4006381333932", quantity = 1,
               price_per_unit= 105.5,discount_rate=0.0)

SECOND_PRODUCT_DAO=SoldProductDAO(id=2, sale_id=4, product_barcode="0000000000000", quantity = 3,
               price_per_unit= 4.5,discount_rate=0.1)

SECOND_PRODUCT_DTO=SoldProductDTO(id=2, sale_id=4, product_barcode="0000000000000", quantity = 3,
               price_per_unit= 4.5,discount_rate=0.1)

THIRD_PRODUCT_DAO=SoldProductDAO(id=3, sale_id=3, product_barcode="4006381333931", quantity = 2,
               price_per_unit= 4,discount_rate=0.5)

THIRD_PRODUCT_DTO=SoldProductDTO(id=3, sale_id=3, product_barcode="4006381333931", quantity = 2,
               price_per_unit= 4,discount_rate=0.5)

NEW_SALE_DAO=SaleDAO(id=1,status="OPEN",discount_rate=0.0,lines=[],
                     created_at=datetime(2025, 10, 30, 12, 34, 56, tzinfo=timezone.utc))

NEW_SALE_DTO=SaleDTO(id=1,status="OPEN",discount_rate=0.0, 
                    created_at=datetime(2025, 10, 30, 12, 34, 56, tzinfo=timezone.utc),lines=[])

FIRST_SALE_DAO=SaleDAO(id=1,status="PENDING",discount_rate=0.0,lines=[],
                     created_at=datetime(2025, 10, 30, 12, 34, 56, tzinfo=timezone.utc),closed_at= datetime(2025, 11, 30, 12, 34, 56, tzinfo=timezone.utc))

FIRST_SALE_DTO=SaleDTO(id=1,status="PENDING",discount_rate=0.0, 
                    created_at=datetime(2025, 10, 30, 12, 34, 56, tzinfo=timezone.utc),closed_at= datetime(2025, 11, 30, 12, 34, 56, tzinfo=timezone.utc),lines=[])

SECOND_SALE_DAO=SaleDAO(id=2,status="PAID",discount_rate=0.5,
                    created_at=datetime(2025, 11, 28, 12, 34, 56, tzinfo=timezone.utc),closed_at= datetime(2025, 11, 30, 12, 34, 56, tzinfo=timezone.utc),
                    lines=[FIRST_PRODUCT_DAO])

SECOND_SALE_DTO=SaleDTO(id=2,status="PAID",discount_rate=0.5,
                    created_at=datetime(2025, 11, 28, 12, 34, 56, tzinfo=timezone.utc),closed_at= datetime(2025, 11, 30, 12, 34, 56, tzinfo=timezone.utc),
                    lines=[FIRST_PRODUCT_DTO])

THIRD_SALE_DAO=SaleDAO(id=3,status="OPEN",discount_rate=0.1,
                     created_at=datetime(2025, 10, 30, 12, 34, 56, tzinfo=timezone.utc),lines=[THIRD_PRODUCT_DAO])

THIRD_SALE_DTO=SaleDTO(id=3,status="OPEN",discount_rate=0.1,
                     created_at=datetime(2025, 10, 30, 12, 34, 56, tzinfo=timezone.utc),lines=[THIRD_PRODUCT_DTO])

FOURTH_SALE_DAO=SaleDAO(id=4,status="PENDING",discount_rate=0.5,
                    created_at=datetime(2025, 11, 28, 12, 34, 56, tzinfo=timezone.utc),closed_at= datetime(2025, 11, 30, 12, 34, 56, tzinfo=timezone.utc),
                    lines=[SECOND_PRODUCT_DAO])

FOURTH_SALE_DTO=SaleDTO(id=4,status="PENDING",discount_rate=0.5,
                    created_at=datetime(2025, 11, 28, 12, 34, 56, tzinfo=timezone.utc),closed_at= datetime(2025, 11, 30, 12, 34, 56, tzinfo=timezone.utc),
                    lines=[SECOND_PRODUCT_DTO])
FIFTH_SALE_DAO=SaleDAO(id=5,status="PAID",discount_rate=0.0,
                    created_at=datetime(2025, 11, 28, 12, 34, 56, tzinfo=timezone.utc),closed_at= datetime(2025, 11, 30, 12, 34, 56, tzinfo=timezone.utc),
                    lines=[FIFTH_PRODUCT_DAO])

FIFTH_SALE_DTO=SaleDTO(id=5,status="PAID",discount_rate=0.0,
                    created_at=datetime(2025, 11, 28, 12, 34, 56, tzinfo=timezone.utc),closed_at= datetime(2025, 11, 30, 12, 34, 56, tzinfo=timezone.utc),
                    lines=[FIFTH_PRODUCT_DTO])

FIRST_PRODUCT_TYPE_DAO=ProductDAO(id=1, description = "hello world", 
                barcode="0123456789111", quantity = 1,note= "None",
                price_per_unit= 5.5,position="1-A-3")

FIRST_PRODUCT_TYPE_DTO=SoldProductDTO(id=1, sale_id=2, product_barcode="0123456789111", quantity = 1,
               price_per_unit= 5.5,discount_rate=0.1)

SECOND_PRODUCT_TYPE_DTO=ProductTypeDTO(id= 2,description="hello world",
    barcode = "0000000000000",price_per_unit= 4.5,note= "None",
    quantity= 10,position= "1-A-2"
)
SECOND_PRODUCT_TYPE_DAO=ProductDAO(id= 2,description = "hello world",
    barcode = "0000000000000",price_per_unit= 4.5,note= "None",
    quantity= 10,position= "1-A-2"
)

THIRD_PRODUCT_TYPE_DAO=ProductDAO(id=3, description = "hello world", 
                barcode="4006381333931", quantity = 1,note= "None",
                price_per_unit= 4,position="1-A-1")

THIRD_PRODUCT_TYPE_DTO=ProductTypeDTO(id=3, description = "hello world", 
                barcode="4006381333931", quantity = 1,note= "None",
                price_per_unit= 4,position="1-A-1")

FIFTH_PRODUCT_TYPE_DAO=ProductDAO(id=5, description = "hello world", 
                barcode="4006381333932", quantity = 1,note= "None",
                price_per_unit= 105.5,position="1-A-5")


FIFTH_PRODUCT_TYPE_DTO=ProductTypeDTO(id=5, description = "hello world", 
                barcode="4006381333932", quantity = 1,note= "None",
                price_per_unit= 105.5,position="1-A-5")


LIST_OF_SALE_DTO=[NEW_SALE_DTO,SECOND_SALE_DTO,THIRD_SALE_DTO]
LIST_OF_SALE_DAO=[NEW_SALE_DAO,SECOND_SALE_DAO,THIRD_SALE_DAO,FOURTH_SALE_DAO,FIFTH_SALE_DAO]
LIST_OF_SALE_PRODUCT_DAO=[FIRST_PRODUCT_DAO,SECOND_PRODUCT_DAO,THIRD_PRODUCT_DAO,FIRST_PRODUCT_DAO]
LIST_OF_PRODUCT_TYPE_DAO=[FIRST_PRODUCT_TYPE_DAO,SECOND_PRODUCT_TYPE_DAO,THIRD_PRODUCT_TYPE_DAO,FIFTH_PRODUCT_TYPE_DAO]

BOOLEAN_RESPONSE_TRUE_DTO=BooleanResponseDTO(success=True)

BOOLEAN_RESPONSE_FALSE_DTO=BooleanResponseDTO(success=False)

#controller=sales_controller
patch_controller="app.controllers.sale_controller"
DATABASE_URL = "sqlite+aiosqlite:///:memory:"

@pytest_asyncio.fixture(scope="function")
async def db_session():
    engine = create_async_engine(DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    SessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)

    async with SessionLocal() as session:
        '''session.add_all(LIST_OF_PRODUCT_TYPE_DAO)
        session.add_all(LIST_OF_SALE_PRODUCT_DAO)
        session.add_all(LIST_OF_SALE_DAO)'''
        yield session
    
    await engine.dispose()
    
@pytest.mark.asyncio
async def test_create_sold_product_controller_ok(db_session):
    repo=SoldProductsRepository(session=db_session)
    controller=SoldProductsController()
    controller.repo=repo
    await db_session.rollback()
    new=SoldProductDTO(id=1,sale_id=1,product_barcode="0000000000000",
                       quantity=1,price_per_unit=0.5,discount_rate=0.0)
    result=await controller.create_sold_product(
        new.id,new.sale_id,new.product_barcode,
        new.quantity,new.price_per_unit
    )
    assert isinstance(result,SoldProductDTO)
    assert result.id==new.id
    assert result.sale_id==new.sale_id
    assert result.product_barcode==new.product_barcode
    assert result.quantity==new.quantity
    assert result.price_per_unit==new.price_per_unit
    assert result.discount_rate==0.0

@pytest.mark.asyncio
async def test_create_sold_product_controller_invalid_input(db_session):
    id=8
    sale_id=id
    quantity=9
    barcode="0000000000000"
    price_unit=8

    repo=SoldProductsRepository(session=db_session)
    controller=SoldProductsController()
    controller.repo=repo
    await db_session.rollback()
    
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
    
    db_check=await db_session.execute(
        select(SoldProductDAO).where(SoldProductDAO.id == 1)
    )
    assert db_check.scalar()==None

@pytest.mark.asyncio
async def test_get_sold_product_by_id_controller_ok(db_session):#control
    id=2
    repo=SoldProductsRepository(session=db_session)
    controller=SoldProductsController()
    controller.repo=repo
    db_session.add(SECOND_PRODUCT_DAO)
    await db_session.commit()

    result=await controller.get_sold_product_by_id(id)

    assert isinstance(result,SoldProductDTO)
    assert result.id==SECOND_PRODUCT_DTO.id
    assert result.sale_id==SECOND_PRODUCT_DTO.sale_id
    assert result.product_barcode==SECOND_PRODUCT_DTO.product_barcode
    assert result.quantity==SECOND_PRODUCT_DTO.quantity
    assert result.price_per_unit==SECOND_PRODUCT_DTO.price_per_unit
    assert result.discount_rate==SECOND_PRODUCT_DTO.discount_rate

@pytest.mark.asyncio
async def test_get_sold_product_by_id_controller_invalid_input(db_session):
    id=-6
    repo=SoldProductsRepository(session=db_session)
    controller=SoldProductsController()
    controller.repo=repo
    await db_session.commit()

    with pytest.raises(BadRequestError) as exc_info:
        await controller.get_sold_product_by_id(id)
    assert exc_info.value.status==400

@pytest.mark.asyncio
async def test_get_sold_product_by_id_controller_not_found(db_session):
    id=6
    repo=SoldProductsRepository(session=db_session)
    controller=SoldProductsController()
    controller.repo=repo
    
    with pytest.raises(NotFoundError) as exc_info:
        await controller.get_sold_product_by_id(id)
    assert exc_info.value.status==404

@pytest.mark.parametrize(
    "productId,productSaleId, soldProduct, code",[
        (1,2,FIRST_PRODUCT_DTO,0),
        (-1,2,FIRST_PRODUCT_DTO,400),
        (1,-2,FIRST_PRODUCT_DTO,400),
        (10,20,FIRST_PRODUCT_DTO,404),
    ]
)
@pytest.mark.asyncio
async def test_get_sold_product(db_session,productId,productSaleId, soldProduct, code):
    repo=SoldProductsRepository(session=db_session)
    controller=SoldProductsController()
    controller.repo=repo
    await controller.create_sold_product(
        soldProduct.id,
        soldProduct.sale_id,
        soldProduct.product_barcode,
        soldProduct.quantity,
        soldProduct.price_per_unit
                                   )
    if(code==0):
        result=await controller.get_sold_product(product_id=productId,
                                              sale_id=productSaleId)
        assert isinstance(result,SoldProductDTO)
        assert result.id==soldProduct.id
        assert result.sale_id==soldProduct.sale_id
        assert result.product_barcode==soldProduct.product_barcode
        assert result.quantity==soldProduct.quantity
        assert result.price_per_unit==soldProduct.price_per_unit
        assert result.discount_rate==0.0
    elif(code==400):
        with pytest.raises(BadRequestError) as exc_info:
            await controller.get_sold_product(product_id=productId,
                                              sale_id=productSaleId)
        assert exc_info.value.status==code
    elif(code==404):
        with pytest.raises(NotFoundError) as exc_info:
            await controller.get_sold_product(product_id=productId,
                                              sale_id=productSaleId)
        assert exc_info.value.status==code

    

@pytest.mark.asyncio
async def test_edit_sold_product_quantity_controller_ok(db_session):
    id=1
    sale_id=2
    quantity=3
    db_session.add(FIRST_PRODUCT_DAO)

    repo=SoldProductsRepository(session=db_session)
    controller=SoldProductsController()
    controller.repo=repo
    await db_session.commit()

    db_check=await db_session.execute(
        select(SoldProductDAO).where(SoldProductDAO.id == id)
    )
    assert db_check!=None
    old_quantity=db_check.scalar().quantity

    result=await controller.edit_sold_product_quantity(id,sale_id,quantity)
    assert result.success
    db_check=await db_session.execute(
        select(SoldProductDAO).where(SoldProductDAO.id == id)
    )
    assert db_check!=None
    assert db_check.scalar().quantity==old_quantity+quantity
    old_quantity+=quantity
    quantity=-2

    result=await controller.edit_sold_product_quantity(id,sale_id,quantity)
    assert result.success

    db_check=await db_session.execute(
        select(SoldProductDAO).where(SoldProductDAO.id == id)
    )
    assert db_check!=None
    assert db_check.scalar().quantity==old_quantity+quantity

    

@pytest.mark.asyncio
async def test_edit_sold_product_quantity_controller_invalid_input(db_session):
    id=9
    sale_id=2
    quantity=45
    repo=SoldProductsRepository(session=db_session)
    controller=SoldProductsController()
    controller.repo=repo
    await db_session.commit()

    id=-9
    with pytest.raises(BadRequestError) as exc_info:
        await controller.edit_sold_product_quantity(id,sale_id,quantity)
    assert exc_info.value.status==400
    id=1
    
    sale_id=-4567895555123
    with pytest.raises(BadRequestError) as exc_info:
        await controller.edit_sold_product_quantity(id,sale_id,quantity)
    assert exc_info.value.status==400
    sale_id=2

@pytest.mark.asyncio
async def test_edit_sold_product_discount_controller_ok(db_session):
    id=FIRST_PRODUCT_DAO.id
    sale_id=FIRST_PRODUCT_DAO.sale_id
    discount=0.5

    repo=SoldProductsRepository(session=db_session)
    controller=SoldProductsController()
    controller.repo=repo

    await controller.create_sold_product(
        FIRST_PRODUCT_DAO.id,
        FIRST_PRODUCT_DAO.sale_id,
        FIRST_PRODUCT_DAO.product_barcode,
        FIRST_PRODUCT_DAO.quantity,
        FIRST_PRODUCT_DAO.price_per_unit
    )

    result=await controller.edit_sold_product_discount(id,sale_id,discount)
    assert result.success

    db_check=await db_session.execute(
        select(SoldProductDAO).where(SoldProductDAO.id == id)
    )
    assert db_check!=None
    assert db_check.scalar().discount_rate==discount

@pytest.mark.asyncio
async def test_edit_sold_product_discount_controller_invalid_input(db_session):
    id=9
    sale_id=9
    discount=0.45
    
    repo=SoldProductsRepository(session=db_session)
    controller=SoldProductsController()
    controller.repo=repo
    await db_session.commit()

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
    
@pytest.mark.asyncio
async def test_remove_sold_product_ok(db_session):
    id=2
    sale_id=4
    barcode="0000000000000"

    repo=SoldProductsRepository(session=db_session)
    controller=SoldProductsController()
    controller.repo=repo

    await controller.create_sold_product(
        SECOND_PRODUCT_DAO.id,
        SECOND_PRODUCT_DAO.sale_id,
        SECOND_PRODUCT_DAO.product_barcode,
        SECOND_PRODUCT_DAO.quantity,
        SECOND_PRODUCT_DAO.price_per_unit
    )
    
    result=await controller.remove_sold_product(sale_id,id)
    assert result is None

@pytest.mark.asyncio
async def test_remove_sold_product_invalid_input(db_session):
    id=1
    sale_id=2
    barcode="0123456789111"
    await db_session.commit()
    repo=SoldProductsRepository(session=db_session)
    controller=SoldProductsController()
    controller.repo=repo

    id=-1
    with pytest.raises(BadRequestError) as exc_info:
        await controller.remove_sold_product(sale_id,id)
    assert exc_info.value.status==400

    id=1
    sale_id=-2
    with pytest.raises(BadRequestError) as exc_info:
        await controller.remove_sold_product(id,sale_id)
    assert exc_info.value.status==400

    sale_id=2