from typing import List
import pytest
from datetime import datetime, timezone
import pytest_asyncio
from unittest.mock import AsyncMock
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
from app.models.DTO.product_dto import ProductCreateDTO, ProductTypeDTO
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

SECOND_PRODUCT_DAO=SoldProductDAO(id=2, sale_id=2, product_barcode="0000000000000", quantity = 3,
               price_per_unit= 4.5,discount_rate=0.1)

SECOND_PRODUCT_DTO=SoldProductDTO(id=2, sale_id=2, product_barcode="0000000000000", quantity = 3,
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

FIRST_PRODUCT_TYPE_DTO=ProductTypeDTO(id=1, description = "hello world", 
                barcode="0123456789111", quantity = 1,note= "None",
                price_per_unit= 5.5,position="1-A-3")

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
async def test_create_sale_controller_ok(db_session):
    await db_session.rollback()
    repo = SalesRepository(session=db_session)
    controller = SalesController()
    controller.repo = repo

    result= await controller.create_sale()
    assert isinstance(result, SaleDTO)
    assert result.id==NEW_SALE_DTO.id
    assert result.status==NEW_SALE_DTO.status
    assert result.lines!=None
    assert result.created_at.replace(tzinfo=timezone.utc)<=datetime.now(timezone.utc).replace(  # type: ignore
                    microsecond=0
                )
    assert result.created_at.replace(tzinfo=timezone.utc)>=START_TEST
@pytest.mark.asyncio
async def test_get_all_sale_controller_ok(db_session):
    await db_session.rollback()
    repo = SalesRepository(session=db_session)
    controller = SalesController()
    controller.repo = repo

    result=await controller.list_sales()
    assert isinstance(result,List)
    assert result==[]

    db_session.add_all(LIST_OF_SALE_DAO)
    await db_session.commit()
    controller.repo = repo

    result=await controller.list_sales()
    for r,l in zip(result,LIST_OF_SALE_DTO):
        assert isinstance(r, SaleDTO)
        assert r.id==l.id
        assert r.status==l.status
        assert r.closed_at==l.closed_at
        assert r.created_at is not None
        for rl,ll in zip(r.lines,l.lines):
            assert rl.id==ll.id
            assert rl.sale_id==ll.sale_id
            assert rl.product_barcode==ll.product_barcode
            assert rl.quantity==ll.quantity
            assert rl.price_per_unit==ll.price_per_unit
            assert rl.discount_rate==ll.discount_rate

@pytest.mark.asyncio
async def test_get_sale_controller_ok(db_session):
    repo = SalesRepository(session=db_session)
    controller = SalesController()
    controller.repo = repo

    sold= SoldProductsController()
    srepo = SoldProductsRepository(session=db_session)
    sold.repo=srepo
    id=1
    
    await controller.create_sale()
    await sold.create_sold_product(
        FIRST_PRODUCT_DAO.id,
        FIRST_PRODUCT_DAO.sale_id,
        FIRST_PRODUCT_DAO.product_barcode,
        FIRST_PRODUCT_DAO.quantity,
        FIRST_PRODUCT_DAO.price_per_unit
    )

    result=await controller.get_sale_by_id(id)
    assert isinstance(result, SaleDTO)
    assert result.id==FIRST_SALE_DTO.id
    assert result.status==NEW_SALE_DTO.status
    assert result.created_at.timestamp() is not None
    for rl,ll in zip(result.lines,SECOND_SALE_DTO.lines):
        assert rl.id==ll.id
        assert rl.sale_id==ll.sale_id
        assert rl.product_barcode==ll.product_barcode
        assert rl.quantity==ll.quantity
        assert rl.price_per_unit==ll.price_per_unit
        assert rl.discount_rate==ll.discount_rate

async def test_get_sale_controller_invalid_input(db_session):
    invalid=-9
    repo = SalesRepository(session=db_session)
    controller = SalesController()
    controller.repo = repo
    with pytest.raises(BadRequestError) as exc_info:
        await controller.get_sale_by_id(invalid)
    assert exc_info.value.status==400

async def test_get_sale_controller_not_found(db_session):
    id=9
    repo = SalesRepository(session=db_session)
    controller = SalesController()
    controller.repo = repo
    with pytest.raises(NotFoundError) as exc_info:
        await controller.get_sale_by_id(id)
    assert exc_info.value.status==404

@pytest.mark.asyncio
async def test_delete_sale_controller_ok(db_session):
    repo = SalesRepository(session=db_session)
    controller = SalesController()
    controller.repo = repo

    sold= SoldProductsController()
    srepo = SoldProductsRepository(session=db_session)
    sold.repo=srepo

    await controller.create_sale()
    await controller.create_sale()
    await controller.create_sale()
    await sold.create_sold_product(
        FIRST_PRODUCT_DAO.id,
        FIRST_PRODUCT_DAO.sale_id,
        FIRST_PRODUCT_DAO.product_barcode,
        FIRST_PRODUCT_DAO.quantity,
        FIRST_PRODUCT_DAO.price_per_unit
    )

    products_controller.update_product_quantity=AsyncMock(
        return_value=BOOLEAN_RESPONSE_TRUE_DTO
    )
    sold_products_controller.edit_sold_product_quantity=products_controller.update_product_quantity=AsyncMock(
        return_value=BOOLEAN_RESPONSE_TRUE_DTO
    )
    sold_products_controller.remove_sold_product=AsyncMock(return_value=None)
    products_controller.update_product_quantity=AsyncMock(return_value=BOOLEAN_RESPONSE_TRUE_DTO)
    await db_session.commit()
    id=3
    result=await controller.delete_sale(id,
                sold_products_controller,products_controller)
    assert result is None
    id=1
    result=await controller.delete_sale(id,sold_products_controller=sold_products_controller,products_controller=products_controller)
    assert result is None 
    id=2
    result=await controller.delete_sale(id,sold_products_controller=sold_products_controller,products_controller=products_controller)
    assert result is None 

@pytest.mark.asyncio
async def test_delete_sale_controller_invalid_input(db_session):
    invalid=-9
    repo = SalesRepository(session=db_session)
    controller = SalesController()
    controller.repo = repo
    
    products_controller.update_product_quantity=AsyncMock(
        return_value=BOOLEAN_RESPONSE_TRUE_DTO
    )
    sold_products_controller.edit_sold_product_quantity=products_controller.update_product_quantity=AsyncMock(
        return_value=BOOLEAN_RESPONSE_TRUE_DTO
    )

    with pytest.raises(BadRequestError) as exc_info:
        await controller.delete_sale(invalid,sold_products_controller,
                                     products_controller)
    assert exc_info.value.status==400

@pytest.mark.asyncio
async def test_delete_sale_controller_not_found(db_session):
    invalid=9
    repo = SalesRepository(session=db_session)
    controller = SalesController()
    controller.repo = repo
    
    products_controller.update_product_quantity=AsyncMock(
        return_value=BOOLEAN_RESPONSE_TRUE_DTO
    )
    sold_products_controller.edit_sold_product_quantity=products_controller.update_product_quantity=AsyncMock(
        return_value=BOOLEAN_RESPONSE_TRUE_DTO
    )

    with pytest.raises(NotFoundError) as exc_info:
        await controller.delete_sale(invalid,sold_products_controller
                                     ,products_controller)
    assert exc_info.value.status==404

@pytest.mark.asyncio
async def test_delete_sale_controller_invalid_status(db_session):
    repo = SalesRepository(session=db_session)
    controller = SalesController()
    controller.repo = repo

    sold= SoldProductsController()
    srepo = SoldProductsRepository(session=db_session)
    sold.repo=srepo
    id=1
    await controller.create_sale()
    await sold.create_sold_product(
        FIRST_PRODUCT_DAO.id,
        id,
        FIRST_PRODUCT_DAO.product_barcode,
        FIRST_PRODUCT_DAO.quantity,
        FIRST_PRODUCT_DAO.price_per_unit
    )

    await controller.close_sale(id,products_controller,sold_products_controller)
    await controller.pay_sale(id,10000)
    products_controller.update_product_quantity=AsyncMock(
        return_value=BOOLEAN_RESPONSE_TRUE_DTO
    )
    sold_products_controller.edit_sold_product_quantity=products_controller.update_product_quantity=AsyncMock(
        return_value=BOOLEAN_RESPONSE_TRUE_DTO
    )

    
    with pytest.raises(InvalidStateError) as exc_info:
        await controller.delete_sale(id,sold_products_controller,products_controller)
    assert exc_info.value.status==420
    db_check=await db_session.execute(
        select(SaleDAO).where(SaleDAO.id == id)
    )
    assert db_check.scalar_one_or_none() is not None

@pytest.mark.parametrize(
        "productSaleId, barcode, amount, productReturn,code",
        [
            (1,FIRST_PRODUCT_DAO.product_barcode,1,FIRST_PRODUCT_DTO,0),
            (-1,FIRST_PRODUCT_DAO.product_barcode,1,FIRST_PRODUCT_DTO,400),
            (1,"",1,FIRST_PRODUCT_DTO,400),
            (1,"000",1,FIRST_PRODUCT_DTO,400),
            (1,FIRST_PRODUCT_DAO.product_barcode,-1,FIRST_PRODUCT_DTO,400),
            (1,FIRST_PRODUCT_DAO.product_barcode,-1,FIRST_PRODUCT_DTO,400),
            (1,FIRST_PRODUCT_DAO.product_barcode,100000,FIRST_PRODUCT_DTO,400),
            (1,SECOND_PRODUCT_DAO.product_barcode,1,None,404)
        ]
)
@pytest.mark.asyncio
async def test_remove_sold_product_quantity(db_session,productSaleId, barcode, amount, productReturn,code):
    repo = SalesRepository(session=db_session)
    controller = SalesController()
    controller.repo = repo
    sold= SoldProductsController()
    srepo = SoldProductsRepository(session=db_session)
    sold.repo=srepo
    id=1
    await controller.create_sale()
    await sold.create_sold_product(
        FIRST_PRODUCT_DAO.id,
        id,
        FIRST_PRODUCT_DAO.product_barcode,
        FIRST_PRODUCT_DAO.quantity,
        FIRST_PRODUCT_DAO.price_per_unit
    )

    products_controller.get_product_by_barcode=AsyncMock(return_value=productReturn)
    sold_products_controller.edit_sold_product_quantity=AsyncMock(return_value=BOOLEAN_RESPONSE_TRUE_DTO)
    products_controller.update_product_quantity=AsyncMock(return_value=BOOLEAN_RESPONSE_TRUE_DTO)

    if(code==0):   
        result=await controller.remove_sold_product_quantity(
            sale_id=productSaleId,
            barcode=barcode,
            amount=amount,
            sold_products_controller=sold_products_controller,
            products_controller=products_controller
            )
        assert result.success
    elif(code==400):
        if(amount>50):
            with pytest.raises(InsufficientStockError) as exc_info:
                await controller.remove_sold_product_quantity(
                sale_id=productSaleId,
                barcode=barcode,
                amount=amount,
                sold_products_controller=sold_products_controller,
                products_controller=products_controller
                )
        else:
            with pytest.raises(BadRequestError) as exc_info:
                await controller.remove_sold_product_quantity(
                sale_id=productSaleId,
                barcode=barcode,
                amount=amount,
                sold_products_controller=sold_products_controller,
                products_controller=products_controller
                ) 
        assert exc_info.value.status==400
    elif(code==404):
        with pytest.raises(NotFoundError) as exc_info:
                await controller.remove_sold_product_quantity(
                sale_id=productSaleId,
                barcode=barcode,
                amount=amount,
                sold_products_controller=sold_products_controller,
                products_controller=products_controller
                ) 
        assert exc_info.value.status==404


    

@pytest.mark.asyncio
async def test_add_product_ok(db_session):
    sale_id=1
    barcode="0123456789111"
    amount=1

    await db_session.commit()
    repo = SalesRepository(session=db_session)
    controller = SalesController()
    controller.repo = repo
    
    products_controller.update_product_quantity=AsyncMock(return_value=BOOLEAN_RESPONSE_TRUE_DTO)
    products_controller.get_product_by_barcode=AsyncMock(return_value=FIRST_PRODUCT_TYPE_DTO)
    sold_products_controller.create_sold_product=AsyncMock(return_value=FIRST_PRODUCT_DTO)
    sold_products_controller.edit_sold_product_quantity=AsyncMock(return_value=BOOLEAN_RESPONSE_TRUE_DTO)
    
    sold= SoldProductsController()
    srepo = SoldProductsRepository(session=db_session)
    sold.repo=srepo
    id=2
    await controller.create_sale()
    await controller.create_sale()
    await sold.create_sold_product(
        THIRD_PRODUCT_DAO.id,
        id,
        THIRD_PRODUCT_DAO.product_barcode,
        THIRD_PRODUCT_DAO.quantity,
        THIRD_PRODUCT_DAO.price_per_unit
    )

    result=await controller.attach_product(sale_id,barcode,amount, products_controller,
        sold_products_controller)
    assert result.success

    sale_id=2
    barcode="4006381333931"
    amount=1

    result=await controller.attach_product(sale_id,barcode,amount, products_controller,
        sold_products_controller)
    assert result.success


@pytest.mark.asyncio
async def test_add_product_controller_invalid_input(db_session):
    invalid=9
    barcode="0123456789111"
    amount=1
    await db_session.commit()
    repo = SalesRepository(session=db_session)
    controller = SalesController()
    controller.repo = repo
    await controller.create_sale()
    products_controller.update_product_quantity=AsyncMock(return_value=BOOLEAN_RESPONSE_TRUE_DTO)
    products_controller.get_product_by_barcode=AsyncMock(return_value=FIRST_PRODUCT_TYPE_DTO)
    sold_products_controller.create_sold_product=AsyncMock(return_value=FIRST_PRODUCT_DTO)


    invalid=-9
    with pytest.raises(BadRequestError) as exc_info:
        await controller.attach_product(invalid,barcode,amount, products_controller,
        sold_products_controller)
    assert exc_info.value.status==400
    id=1

    barcode=""
    with pytest.raises(BadRequestError) as exc_info:
        await controller.attach_product(id,barcode,amount, products_controller,
        sold_products_controller)
    assert exc_info.value.status==400

    barcode="000"
    with pytest.raises(BadRequestError) as exc_info:
        await controller.attach_product(id,barcode,amount, products_controller,
        sold_products_controller)
    assert exc_info.value.status==400
    barcode="0123456789111"
    
    amount=-15
    with pytest.raises(BadRequestError) as exc_info:
        await controller.attach_product(id,barcode,amount, products_controller,
        sold_products_controller)
    assert exc_info.value.status==400
    amount=9

    amount=5100
    with pytest.raises(InsufficientStockError) as exc_info:
        await controller.attach_product(id,barcode,amount, products_controller,
        sold_products_controller)
    assert exc_info.value.status==400

    db_check=await db_session.execute(
        select(SaleDAO).where(SaleDAO.id == id)
    )
    assert db_check is not None
    assert db_check.scalar().lines ==[]

@pytest.mark.asyncio
async def test_add_product_controller_not_found(db_session):
    id=9
    barcode="0123456789111"
    amount=1
    await db_session.commit()
    repo = SalesRepository(session=db_session)
    controller = SalesController()
    controller.repo = repo
    
    products_controller.update_product_quantity=AsyncMock(return_value=BOOLEAN_RESPONSE_TRUE_DTO)
    products_controller.get_product_by_barcode=AsyncMock(side_effect=NotFoundError("Product not found"))
    sold_products_controller.create_sold_product=AsyncMock(return_value=FIRST_PRODUCT_DTO)
    await controller.create_sale()

    id=400
    with pytest.raises(NotFoundError) as exc_info:
        await controller.attach_product(id,barcode,amount, products_controller,
        sold_products_controller)
    assert exc_info.value.status==404
    id=1

    barcode="1234567890128"
    with pytest.raises(NotFoundError) as exc_info:
        await controller.attach_product(id,barcode,amount, products_controller,
        sold_products_controller)
    assert exc_info.value.status==404
    db_check=await db_session.execute(
        select(SaleDAO).where(SaleDAO.id == id)
    )
    assert db_check is not None
    assert db_check.scalar().lines ==[]




@pytest.mark.asyncio
async def test_add_product_controller_invalid_status(db_session):
    sale_id=1
    barcode="0123456789111"
    amount=1
    await db_session.commit()
    repo = SalesRepository(session=db_session)
    controller = SalesController()
    controller.repo = repo
    
    products_controller.update_product_quantity=AsyncMock(return_value=BOOLEAN_RESPONSE_TRUE_DTO)
    products_controller.get_product_by_barcode=AsyncMock(return_value=FIRST_PRODUCT_TYPE_DTO)
    sold_products_controller.create_sold_product=AsyncMock(return_value=FIRST_PRODUCT_DTO)
    sold= SoldProductsController()
    srepo = SoldProductsRepository(session=db_session)
    sold.repo=srepo
    id=1
    await controller.create_sale()
    await sold.create_sold_product(
        FIRST_PRODUCT_DAO.id,
        id,
        FIRST_PRODUCT_DAO.product_barcode,
        FIRST_PRODUCT_DAO.quantity,
        FIRST_PRODUCT_DAO.price_per_unit
    )
    await controller.close_sale(id,products_controller,sold_products_controller)

    with pytest.raises(InvalidStateError) as exc_info:
        await controller.attach_product(sale_id,barcode,amount, products_controller,
        sold_products_controller)
    assert exc_info.value.status==420

    db_check=await db_session.execute(
        select(SaleDAO).where(SaleDAO.id == sale_id)
    )
    assert db_check is not None
    assert len(db_check.scalar().lines)==1

    await controller.pay_sale(id,10000)
    with pytest.raises(InvalidStateError) as exc_info:
        await controller.attach_product(sale_id,barcode,amount, products_controller,
        sold_products_controller)
    assert exc_info.value.status==420

    db_check=await db_session.execute(
        select(SaleDAO).where(SaleDAO.id == sale_id)
    )
    assert db_check is not None
    assert len(db_check.scalar().lines)==1
    



@pytest.mark.asyncio
async def test_edit_product_controller_ok(db_session):
    sale_id=1
    barcode="4006381333931"
    amount=1
    repo = SalesRepository(session=db_session)
    controller = SalesController()
    controller.repo = repo

    sold= SoldProductsController()
    srepo = SoldProductsRepository(session=db_session)
    sold.repo=srepo

    await controller.create_sale()
    await sold.create_sold_product(
        FIRST_PRODUCT_DAO.id,
        sale_id,
        barcode,
        FIRST_PRODUCT_DAO.quantity+10,
        FIRST_PRODUCT_DAO.price_per_unit
    )
    await db_session.commit()
    db_check=await db_session.execute(
        select(SaleDAO).where(SaleDAO.id == sale_id)
    )
    assert db_check is not None
    old_amount=db_check.scalar().lines[0].quantity

    products_controller.get_product_by_barcode= AsyncMock(return_value=THIRD_PRODUCT_TYPE_DTO)
    sold_products_controller.edit_sold_product_quantity=AsyncMock(return_value=THIRD_PRODUCT_TYPE_DTO)
    products_controller.update_product_quantity=AsyncMock(return_value=THIRD_PRODUCT_TYPE_DTO)

    result=await controller.edit_sold_product_quantity(sale_id, barcode, 
        amount, sold_products_controller,products_controller)

    assert result.success


    result=await controller.edit_sold_product_quantity(sale_id, barcode, 
        amount, sold_products_controller,products_controller)

    assert result.success

    amount=-1
    result=await controller.edit_sold_product_quantity(sale_id, barcode, 
        amount, sold_products_controller,products_controller)

    assert result.success




@pytest.mark.asyncio
async def test_edit_product_controller_invalid_input(db_session):
    sale_id=1
    barcode="4006381333931"
    amount=1

    repo = SalesRepository(session=db_session)
    controller = SalesController()
    controller.repo = repo
    await db_session.commit()
    products_controller.get_product_by_barcode= AsyncMock(return_value=THIRD_PRODUCT_TYPE_DTO)
    sold_products_controller.edit_sold_product_quantity=AsyncMock(return_value=THIRD_PRODUCT_TYPE_DTO)
    products_controller.update_product_quantity=AsyncMock(return_value=THIRD_PRODUCT_TYPE_DTO)

    sold= SoldProductsController()
    srepo = SoldProductsRepository(session=db_session)
    sold.repo=srepo

    await controller.create_sale()
    await sold.create_sold_product(
        FIRST_PRODUCT_DAO.id,
        sale_id,
        barcode,
        FIRST_PRODUCT_DAO.quantity+10,
        FIRST_PRODUCT_DAO.price_per_unit
    )

    sale_id=-9
    with pytest.raises(BadRequestError) as exc_info:
        await controller.edit_sold_product_quantity(sale_id, barcode, 
        amount, sold_products_controller,products_controller)
    assert exc_info.value.status==400

    sale_id=1
    barcode=""
    with pytest.raises(BadRequestError) as exc_info:
        await controller.edit_sold_product_quantity(sale_id, barcode, 
        amount, sold_products_controller,products_controller)
    assert exc_info.value.status==400

    barcode="000"
    with pytest.raises(BadRequestError) as exc_info:
        await controller.edit_sold_product_quantity(sale_id, barcode, 
        amount, sold_products_controller,products_controller)
    assert exc_info.value.status==400

    barcode="4006381333931"
    amount=5100
    with pytest.raises(InsufficientStockError) as exc_info:
        await controller.edit_sold_product_quantity(sale_id, barcode, 
        amount, sold_products_controller,products_controller)
    assert exc_info.value.status==400

    amount=-5100
    with pytest.raises(InsufficientStockError) as exc_info:
        await controller.edit_sold_product_quantity(sale_id, barcode, 
        amount, sold_products_controller,products_controller)
    assert exc_info.value.status==400

@pytest.mark.asyncio
async def test_edit_product_controller_invalid_status(db_session):
    sale_id=2
    barcode="0123456789111"
    amount=1

    repo = SalesRepository(session=db_session)
    controller = SalesController()
    controller.repo = repo
    await db_session.commit()
    products_controller.get_product_by_barcode= AsyncMock(return_value=THIRD_PRODUCT_TYPE_DTO)
    sold_products_controller.edit_sold_product_quantity=AsyncMock(return_value=THIRD_PRODUCT_TYPE_DTO)
    products_controller.update_product_quantity=AsyncMock(return_value=THIRD_PRODUCT_TYPE_DTO)

    
    with pytest.raises(InvalidStateError) as exc_info:
        await controller.edit_sold_product_quantity(sale_id, barcode, 
        amount, sold_products_controller,products_controller) 
    assert exc_info.value.status==420


    sale_id=4
    with pytest.raises(InvalidStateError) as exc_info:
        await controller.edit_sold_product_quantity(sale_id, barcode, 
        amount, sold_products_controller=sold_products_controller,products_controller=products_controller) 
    assert exc_info.value.status==420


@pytest.mark.asyncio
async def test_edit_product_controller_not_found(db_session):
    sale_id=3
    barcode="4006381333931"
    amount=1

    repo = SalesRepository(session=db_session)
    controller = SalesController()
    controller.repo = repo
    
    products_controller.get_product_by_barcode= AsyncMock(return_value=THIRD_PRODUCT_TYPE_DTO)
    sold_products_controller.edit_sold_product_quantity=AsyncMock(return_value=THIRD_PRODUCT_TYPE_DTO)
    products_controller.update_product_quantity=AsyncMock(return_value=THIRD_PRODUCT_TYPE_DTO)

    sale_id=4555
    with pytest.raises(NotFoundError) as exc_info:
        await controller.edit_sold_product_quantity(sale_id, barcode, 
        amount, sold_products_controller=sold_products_controller,products_controller=products_controller) 
    assert exc_info.value.status==404
    products_controller.get_product_by_barcode= AsyncMock(side_effect=NotFoundError("Product not found"))
    sale_id=3
    barcode="0000000000000"
    with pytest.raises(NotFoundError) as exc_info:
        await controller.edit_sold_product_quantity(sale_id, barcode, 
        amount, sold_products_controller=sold_products_controller,products_controller=products_controller) 
    assert exc_info.value.status==404


@pytest.mark.asyncio
async def test_edit_sale_discount_controller_ok(db_session):
    sale_id=1
    discount_rate=0.26
    await db_session.commit()
    repo = SalesRepository(session=db_session)
    controller = SalesController()
    controller.repo = repo
    await controller.create_sale()
    result=await controller.edit_sale_discount(sale_id,discount_rate)
    assert result.success

    db_check=await db_session.execute(
        select(SaleDAO).where(SaleDAO.id == sale_id)
    )
    assert db_check.scalar().discount_rate==discount_rate

@pytest.mark.asyncio
async def test_edit_sale_discount_controller_invalid_input(db_session):
    sale_id=1
    discount_rate=0.1
    await db_session.commit()
    repo = SalesRepository(session=db_session)
    controller = SalesController()
    controller.repo = repo

    await controller.create_sale()
    db_check=await db_session.execute(
        select(SaleDAO).where(SaleDAO.id == sale_id)
    )
    old_discount=db_check.scalar().discount_rate

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

    db_check=await db_session.execute(
        select(SaleDAO).where(SaleDAO.id == sale_id)
    )
    assert db_check.scalar().discount_rate==old_discount

@pytest.mark.asyncio
async def test_edit_sale_discount_controller_not_found(db_session):
    sale_id=881
    discount_rate=0.1

    repo = SalesRepository(session=db_session)
    controller = SalesController()
    controller.repo = repo

    with pytest.raises(NotFoundError) as exc_info:
        await controller.edit_sale_discount(sale_id,discount_rate)
    assert exc_info.value.status==404


@pytest.mark.asyncio
async def test_edit_sale_discount_invalid_status(db_session):
    sale_id=1
    discount_rate=0.1

    repo = SalesRepository(session=db_session)
    controller = SalesController()
    controller.repo = repo
    sold= SoldProductsController()
    srepo = SoldProductsRepository(session=db_session)
    sold.repo=srepo

    await controller.create_sale()
    await sold.create_sold_product(
        FIRST_PRODUCT_DAO.id,
        sale_id,
        FIRST_PRODUCT_DAO.product_barcode,
        FIRST_PRODUCT_DAO.quantity,
        FIRST_PRODUCT_DAO.price_per_unit
    )
    await controller.close_sale(sale_id,products_controller,sold_products_controller)

    db_check=await db_session.execute(
        select(SaleDAO).where(SaleDAO.id == sale_id)
    )
    old_discount=db_check.scalar().discount_rate

    
    with pytest.raises(InvalidStateError) as exc_info:
        await controller.edit_sale_discount(sale_id,discount_rate)
    assert exc_info.value.status==420

    db_check=await db_session.execute(
        select(SaleDAO).where(SaleDAO.id == sale_id)
    )
    assert db_check is not None
    assert old_discount==db_check.scalar().discount_rate

    sale_id=1
    await controller.pay_sale(sale_id,10000)
    db_check=await db_session.execute(
        select(SaleDAO).where(SaleDAO.id == sale_id)
    )
    old_discount=db_check.scalar().discount_rate

    with pytest.raises(InvalidStateError) as exc_info:
        await controller.edit_sale_discount(sale_id,discount_rate)
    assert exc_info.value.status==420

    db_check=await db_session.execute(
        select(SaleDAO).where(SaleDAO.id == sale_id)
    )
    assert db_check is not None
    assert old_discount==db_check.scalar().discount_rate


@pytest.mark.asyncio
async def test_edit_product_discount_controller_ok(db_session):
    sale_id=1
    barcode="4006381333931"
    discount_rate=0.26

    repo = SalesRepository(session=db_session)
    controller = SalesController()
    controller.repo = repo

    sold= SoldProductsController()
    srepo = SoldProductsRepository(session=db_session)
    sold.repo=srepo

    await controller.create_sale()
    await sold.create_sold_product(
        FIRST_PRODUCT_DAO.id,
        sale_id,
        barcode,
        FIRST_PRODUCT_DAO.quantity,
        FIRST_PRODUCT_DAO.price_per_unit
    )

    sold_products_controller.edit_sold_product_discount=AsyncMock(result_value=BOOLEAN_RESPONSE_TRUE_DTO)

    result=await controller.edit_product_discount(sale_id,barcode,discount_rate,sold_products_controller)
    assert result.success

@pytest.mark.asyncio
async def test_edit_product_discount_controller_invalid_input(db_session):
    sale_id=1
    barcode="4006381333931"
    discount_rate=0.1

    sold_products_controller.edit_sold_product_discount=AsyncMock(result_value=BOOLEAN_RESPONSE_TRUE_DTO)

    repo = SalesRepository(session=db_session)
    controller = SalesController()
    controller.repo = repo
    sold= SoldProductsController()
    srepo = SoldProductsRepository(session=db_session)
    sold.repo=srepo

    await controller.create_sale()
    await sold.create_sold_product(
        FIRST_PRODUCT_DAO.id,
        sale_id,
        barcode,
        FIRST_PRODUCT_DAO.quantity,
        FIRST_PRODUCT_DAO.price_per_unit
    )

    sale_id=-9
    with pytest.raises(BadRequestError) as exc_info:
        await controller.edit_product_discount(sale_id,barcode,discount_rate,sold_products_controller)
    assert exc_info.value.status==400

    sale_id=1
    barcode=""
    with pytest.raises(BadRequestError) as exc_info:
        await controller.edit_product_discount(sale_id,barcode,discount_rate,sold_products_controller)
    assert exc_info.value.status==400

    barcode="000"
    with pytest.raises(BadRequestError) as exc_info:
        await controller.edit_product_discount(sale_id,barcode,discount_rate,sold_products_controller)
    assert exc_info.value.status==400

    barcode="4006381333931"
    discount_rate=5100
    with pytest.raises(BadRequestError) as exc_info:
        await controller.edit_product_discount(sale_id,barcode,discount_rate,sold_products_controller)
    assert exc_info.value.status==400

    discount_rate=-0.5100
    with pytest.raises(BadRequestError) as exc_info:
        await controller.edit_product_discount(sale_id,barcode,discount_rate,sold_products_controller)
    assert exc_info.value.status==400

@pytest.mark.asyncio
async def test_edit_product_discount_controller_not_found(db_session):
    sale_id=3
    barcode="4006381333931"
    discount_rate=0.1

    sold_products_controller.edit_sold_product_discount=AsyncMock(result_value=BOOLEAN_RESPONSE_TRUE_DTO)

    repo = SalesRepository(session=db_session)
    controller = SalesController()
    controller.repo = repo

    sale_id=10
    with pytest.raises(NotFoundError) as exc_info:
        await controller.edit_product_discount(sale_id,barcode,discount_rate,sold_products_controller)
    assert exc_info.value.status==404

    sale_id=3
    barcode="0000000000000"
    with pytest.raises(NotFoundError) as exc_info:
        await controller.edit_product_discount(sale_id,barcode,discount_rate,sold_products_controller)
    assert exc_info.value.status==404

    
@pytest.mark.asyncio
async def test_edit_product_controller_invalid_status(db_session):
    sale_id=1
    barcode="0123456789111"
    discount_rate=0.1
    await db_session.commit()

    repo = SalesRepository(session=db_session)
    controller = SalesController()
    controller.repo = repo
    
    sold= SoldProductsController()
    srepo = SoldProductsRepository(session=db_session)
    sold.repo=srepo

    await controller.create_sale()
    await sold.create_sold_product(
        FIRST_PRODUCT_DAO.id,
        sale_id,
        FIRST_PRODUCT_DAO.product_barcode,
        FIRST_PRODUCT_DAO.quantity,
        FIRST_PRODUCT_DAO.price_per_unit
    )
    await controller.close_sale(sale_id,products_controller,sold_products_controller)

    with pytest.raises(InvalidStateError) as exc_info:
        await controller.edit_product_discount(sale_id,barcode,discount_rate,sold_products_controller)
    assert exc_info.value.status==420


    sale_id=1
    await controller.pay_sale(sale_id=sale_id,cash_amount=1000)
    with pytest.raises(InvalidStateError) as exc_info:
        await controller.edit_product_discount(sale_id,barcode,discount_rate,sold_products_controller)
    assert exc_info.value.status==420


@pytest.mark.asyncio
async def test_close_sale_controller_ok(db_session):
    sale_id=1

    repo = SalesRepository(session=db_session)
    controller = SalesController()
    controller.repo = repo

    products_controller.update_product_quantity=AsyncMock(
        return_value=BOOLEAN_RESPONSE_TRUE_DTO
    )
    sold_products_controller.edit_sold_product_quantity=products_controller.update_product_quantity=AsyncMock(
        return_value=BOOLEAN_RESPONSE_TRUE_DTO
    )
    await controller.create_sale()
    result=await controller.close_sale(sale_id,
            products_controller,sold_products_controller)
    assert result.success

    sold= SoldProductsController()
    srepo = SoldProductsRepository(session=db_session)
    sold.repo=srepo

    await controller.create_sale()
    await sold.create_sold_product(
        FIRST_PRODUCT_DAO.id,
        sale_id,
        FIRST_PRODUCT_DAO.product_barcode,
        FIRST_PRODUCT_DAO.quantity,
        FIRST_PRODUCT_DAO.price_per_unit
    )
    sale_id=1
    result=await controller.close_sale(sale_id,
            products_controller,SalesController)
    assert result.success


@pytest.mark.asyncio 
async def test_close_sale_controller_invalid_input(db_session):
    sale_id=-15
    await db_session.commit()

    repo = SalesRepository(session=db_session)
    controller = SalesController()
    controller.repo = repo

    products_controller.update_product_quantity=AsyncMock(
        return_value=BOOLEAN_RESPONSE_TRUE_DTO
    )
    sold_products_controller.edit_sold_product_quantity=products_controller.update_product_quantity=AsyncMock(
        return_value=BOOLEAN_RESPONSE_TRUE_DTO
    )
    
    with pytest.raises(BadRequestError) as exc_info:
        await controller.close_sale(sale_id,products_controller=products_controller,sold_products_controller=sold_products_controller)
    assert exc_info.value.status==400


@pytest.mark.asyncio 
async def test_close_sale_controller_not_found(db_session):
    sale_id=15
    await db_session.commit()

    repo = SalesRepository(session=db_session)
    controller = SalesController()
    controller.repo = repo

    products_controller.update_product_quantity=AsyncMock(
        return_value=BOOLEAN_RESPONSE_TRUE_DTO
    )
    sold_products_controller.edit_sold_product_quantity=products_controller.update_product_quantity=AsyncMock(
        return_value=BOOLEAN_RESPONSE_TRUE_DTO
    )

    with pytest.raises(NotFoundError) as exc_info:
        await controller.close_sale(sale_id,products_controller=products_controller,sold_products_controller=sold_products_controller)
    assert exc_info.value.status==404

@pytest.mark.asyncio
async def test_close_sale_controller_invalid_status(db_session):
    sale_id=1

    repo = SalesRepository(session=db_session)
    controller = SalesController()
    controller.repo = repo

    sold= SoldProductsController()
    srepo = SoldProductsRepository(session=db_session)
    sold.repo=srepo

    await controller.create_sale()
    await sold.create_sold_product(
        FIRST_PRODUCT_DAO.id,
        sale_id,
        FIRST_PRODUCT_DAO.product_barcode,
        FIRST_PRODUCT_DAO.quantity,
        FIRST_PRODUCT_DAO.price_per_unit
    )
    await controller.close_sale(sale_id,products_controller=products_controller,sold_products_controller=sold_products_controller)


    products_controller.update_product_quantity=AsyncMock(
        return_value=BOOLEAN_RESPONSE_TRUE_DTO
    )
    sold_products_controller.edit_sold_product_quantity=products_controller.update_product_quantity=AsyncMock(
        return_value=BOOLEAN_RESPONSE_TRUE_DTO
    )

    with pytest.raises(InvalidStateError) as exc_info:
        await controller.close_sale(sale_id,products_controller=products_controller,sold_products_controller=sold_products_controller)
    assert exc_info.value.status==420
    
    await controller.pay_sale(sale_id,1000) 

    with pytest.raises(InvalidStateError) as exc_info:
        await controller.close_sale(sale_id,products_controller=products_controller,sold_products_controller=sold_products_controller)
    assert exc_info.value.status==420

@pytest.mark.asyncio
async def test_paid_sale_controller_ok(db_session):
    sale_id=1
    cash_amount=200
    await db_session.commit()
    repo = SalesRepository(session=db_session)
    controller = SalesController()
    controller.repo = repo
    sold= SoldProductsController()
    srepo = SoldProductsRepository(session=db_session)
    sold.repo=srepo

    await controller.create_sale()
    await sold.create_sold_product(
        FIRST_PRODUCT_DAO.id,
        sale_id,
        FIRST_PRODUCT_DAO.product_barcode,
        FIRST_PRODUCT_DAO.quantity,
        FIRST_PRODUCT_DAO.price_per_unit
    )
    await controller.close_sale(sale_id,products_controller=products_controller,sold_products_controller=sold_products_controller)

    result=await controller.pay_sale(sale_id,cash_amount)
    assert result.change==194.5


@pytest.mark.asyncio 
async def test_paid_sale_controller_invalid_input(db_session):
    sale_id=1
    cash_amount=200
    await db_session.commit()
    repo = SalesRepository(session=db_session)
    controller = SalesController()
    controller.repo = repo
    sold= SoldProductsController()
    srepo = SoldProductsRepository(session=db_session)
    sold.repo=srepo

    await controller.create_sale()
    await sold.create_sold_product(
        FIRST_PRODUCT_DAO.id,
        sale_id,
        FIRST_PRODUCT_DAO.product_barcode,
        FIRST_PRODUCT_DAO.quantity,
        FIRST_PRODUCT_DAO.price_per_unit
    )
    await controller.close_sale(sale_id,products_controller=products_controller,sold_products_controller=sold_products_controller)

    sale_id=-5
    with pytest.raises(BadRequestError) as exc_info:
        await controller.pay_sale(sale_id,cash_amount)
    assert exc_info.value.status==400
    sale_id=1

    cash_amount=-9
    with pytest.raises(BadRequestError) as exc_info:
        await controller.pay_sale(sale_id,cash_amount)
    assert exc_info.value.status==400

    cash_amount=0.01
    with pytest.raises(BadRequestError) as exc_info:
        await controller.pay_sale(sale_id,cash_amount)
    assert exc_info.value.status==400


@pytest.mark.asyncio 
async def test_paid_sale_controller_not_found(db_session):
    sale_id=15
    cash_amount=200
    await db_session.commit()
    repo = SalesRepository(session=db_session)
    controller = SalesController()
    controller.repo = repo

    sale_id=50
    with pytest.raises(NotFoundError) as exc_info:
        await controller.pay_sale(sale_id,cash_amount)
    assert exc_info.value.status==404

@pytest.mark.asyncio
async def test_paid_sale_controller_invalid_status(db_session):
    sale_id=1
    cash_amount=200

    repo = SalesRepository(session=db_session)
    controller = SalesController()
    controller.repo = repo
    await controller.create_sale()    
    with pytest.raises(InvalidStateError) as exc_info:
        await controller.pay_sale(sale_id,cash_amount)
    assert exc_info.value.status==420

    sale_id=1
    sold= SoldProductsController()
    srepo = SoldProductsRepository(session=db_session)
    sold.repo=srepo

    await controller.create_sale()
    await sold.create_sold_product(
        FIRST_PRODUCT_DAO.id,
        sale_id,
        FIRST_PRODUCT_DAO.product_barcode,
        FIRST_PRODUCT_DAO.quantity,
        FIRST_PRODUCT_DAO.price_per_unit
    )
    await controller.close_sale(sale_id,products_controller=products_controller,sold_products_controller=sold_products_controller)
    await controller.pay_sale(sale_id,cash_amount)
    with pytest.raises(InvalidStateError) as exc_info:
        await controller.pay_sale(sale_id,cash_amount)
    assert exc_info.value.status==420
    

@pytest.mark.asyncio 
async def test_get_point_controller_ok(db_session):
    sale_id=1
    await db_session.commit()
    repo = SalesRepository(session=db_session)
    controller = SalesController()
    controller.repo = repo
    await controller.create_sale()
    sold= SoldProductsController()
    srepo = SoldProductsRepository(session=db_session)
    sold.repo=srepo
    await sold.create_sold_product(
        FIRST_PRODUCT_DAO.id,
        sale_id,
        FIRST_PRODUCT_DAO.product_barcode,
        FIRST_PRODUCT_DAO.quantity+100,
        FIRST_PRODUCT_DAO.price_per_unit
    )
    await controller.close_sale(sale_id,products_controller=products_controller,sold_products_controller=sold_products_controller)
    await controller.pay_sale(sale_id,10000)
    result=await controller.get_points(sale_id)
    assert result.points==55

@pytest.mark.asyncio
async def test_get_point_controller_invalid_input(db_session):
    
    sale_id=-5
    await db_session.commit()
    repo = SalesRepository(session=db_session)
    controller = SalesController()
    controller.repo = repo

    controller.repo = repo
    await controller.create_sale()
    sold= SoldProductsController()
    srepo = SoldProductsRepository(session=db_session)
    sold.repo=srepo
    await sold.create_sold_product(
        FIRST_PRODUCT_DAO.id,
        1,
        FIRST_PRODUCT_DAO.product_barcode,
        FIRST_PRODUCT_DAO.quantity+100,
        FIRST_PRODUCT_DAO.price_per_unit
    )
    await controller.close_sale(1,products_controller=products_controller,sold_products_controller=sold_products_controller)
    await controller.pay_sale(1,10000)
    
    with pytest.raises(BadRequestError) as exc_info:
        await controller.get_points(sale_id)
    assert exc_info.value.status==400

@pytest.mark.asyncio
async def test_get_point_controller_not_found(db_session):
    
    sale_id=45
    await db_session.commit()
    repo = SalesRepository(session=db_session)
    controller = SalesController()
    controller.repo = repo
    
    with pytest.raises(NotFoundError) as exc_info:
        await controller.get_points(sale_id)
    assert exc_info.value.status==404

@pytest.mark.asyncio
async def test_get_point_controller_invalid_status(db_session):
    sale_id=1
    await db_session.commit()
    repo = SalesRepository(session=db_session)
    controller = SalesController()
    controller.repo = repo
    await controller.create_sale()
    with pytest.raises(InvalidStateError) as exc_info:
        await controller.get_points(sale_id)
    assert exc_info.value.status==420

    sale_id=1
    sold= SoldProductsController()
    srepo = SoldProductsRepository(session=db_session)
    sold.repo=srepo
    await sold.create_sold_product(
        FIRST_PRODUCT_DAO.id,
        1,
        FIRST_PRODUCT_DAO.product_barcode,
        FIRST_PRODUCT_DAO.quantity+100,
        FIRST_PRODUCT_DAO.price_per_unit
    )
    await controller.close_sale(1,products_controller=products_controller,sold_products_controller=sold_products_controller)
    with pytest.raises(InvalidStateError) as exc_info:
        await controller.get_points(sale_id)
    assert exc_info.value.status==420