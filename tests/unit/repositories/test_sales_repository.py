from typing import List
from unittest.mock import AsyncMock, MagicMock
import pytest

from app.models.DAO.sale_dao import SaleDAO
from app.models.DAO.sold_product_dao import SoldProductDAO
from app.models.DTO.boolean_response_dto import BooleanResponseDTO
from app.models.DTO.product_dto import ProductTypeDTO
from app.models.DTO.sale_dto import SaleDTO
from app.models.DTO.sold_product_dto import SoldProductDTO
from app.models.errors.bad_request import BadRequestError
from app.models.errors.conflict_error import ConflictError
from app.models.errors.invalid_state_error import InvalidStateError
from app.models.errors.notfound_error import NotFoundError
from app.repositories.sales_repository import SalesRepository
from app.repositories.sold_products_repository import SoldProductsRepository


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
LIST_OF_SALE_DAO=[NEW_SALE_DAO,SECOND_SALE_DAO,THIRD_SALE_DAO]

BOOLEAN_RESPONSE_TRUE_DTO=BooleanResponseDTO(success=True)

BOOLEAN_RESPONSE_FALSE_DTO=BooleanResponseDTO(success=False)


@pytest.fixture
def mock_session():
    session = AsyncMock()
    session.__aenter__.return_value = session
    session.add = MagicMock()
    session.delete = AsyncMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    return session

@pytest.fixture
def repo(mock_session):
    return SalesRepository(session=mock_session)



@pytest.mark.asyncio
async def test_create_sale_ok(repo, mock_session):
    result=await repo.create_sale()

    assert result.status=='OPEN'
    assert result.discount_rate==0.0
    assert result.lines==[]

    mock_session.add.assert_called_once()
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once()

@pytest.mark.asyncio
async def test_list_sales_full(repo, mock_session):

    mock_result=MagicMock()
    mock_result.scalars.return_value=LIST_OF_SALE_DAO
    mock_session.execute.return_value = mock_result

    result=await repo.list_sales()
    assert isinstance(result,List)
    for r,l in zip(result,LIST_OF_SALE_DAO):
        assert isinstance(r, SaleDAO)
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
        
    mock_session.execute.assert_called_once()

@pytest.mark.asyncio
async def test_list_sales_empty(repo,mock_session):

    mock_result = MagicMock()
    mock_session.execute.return_value = mock_result
    mock_result.scalars.return_value = []
    result= await repo.list_sales()

    assert result==[]
    mock_session.execute.assert_called_once()

@pytest.mark.asyncio
async def test_get_sale_by_id_ok(repo,mock_session):
    id=2
    mock_result = MagicMock()
    mock_session.execute.return_value = mock_result
    mock_result.scalars.return_value.first.return_value = SECOND_SALE_DAO
    result=await repo.get_sale_by_id(id)

    assert isinstance(result, SaleDAO)
    assert result.id==SECOND_SALE_DAO.id
    assert result.status==SECOND_SALE_DAO.status
    assert result.closed_at==SECOND_SALE_DAO.closed_at
    assert result.created_at==SECOND_SALE_DAO.created_at
    for rl,ll in zip(result.lines,SECOND_SALE_DAO.lines):
        assert rl.id==ll.id
        assert rl.sale_id==ll.sale_id
        assert rl.product_barcode==ll.product_barcode
        assert rl.quantity==ll.quantity
        assert rl.price_per_unit==ll.price_per_unit
        assert rl.discount_rate==ll.discount_rate
        
    mock_session.execute.assert_called_once()

@pytest.mark.asyncio
async def test_get_sale_by_id_not_found(repo,mock_session):
    id=20
    mock_result = MagicMock()
    mock_session.execute.return_value = mock_result
    mock_result.scalars.return_value.first.return_value = None
    with pytest.raises(NotFoundError)as exc_info:
        await repo.get_sale_by_id(id)
    assert exc_info.value.status==404

@pytest.mark.asyncio
async def test_delete_sale_ok(repo,mock_session):
    id=1
    mock_result = MagicMock()
    mock_session.execute.return_value = mock_result
    mock_result.scalar.return_value= NEW_SALE_DAO
    
    result=await repo.delete_sale(id)
    assert result.success

    mock_session.delete.assert_called_once_with(NEW_SALE_DAO)
    mock_session.commit.assert_called_once()



@pytest.mark.asyncio
async def test_delete_sale_not_found(repo,mock_session):
    id=100
    mock_result = MagicMock()
    mock_session.execute.return_value = mock_result
    mock_result.scalar.return_value= None

    with pytest.raises(NotFoundError)as exc_info:
        await repo.delete_sale(id)
    assert exc_info.value.status==404

@pytest.mark.asyncio
async def test_edit_sale_discount_ok(repo,mock_session):
    sale_id=1
    discount=0.23

    old_discount=NEW_SALE_DAO.discount_rate
    mock_result = MagicMock()
    mock_session.execute.return_value = mock_result
    mock_result.scalar.return_value= NEW_SALE_DAO

    result=await repo.edit_sale_discount(sale_id,discount)

    assert result.success
    assert NEW_SALE_DAO.discount_rate==discount
    NEW_SALE_DAO.discount_rate=old_discount

    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once()


@pytest.mark.asyncio
async def test_edit_sale_discount_not_found(repo,mock_session):
    sale_id=100
    discount=0.23

    mock_result = MagicMock()
    mock_session.execute.return_value = mock_result
    mock_result.scalar.return_value= None

    with pytest.raises(NotFoundError)as exc_info:
        await repo.edit_sale_discount(sale_id,discount)
    assert exc_info.value.status==404

@pytest.mark.asyncio
async def test_edit_sale_discount_invalid_status(repo,mock_session):
    sale_id=2
    discount=0.23

    mock_result = MagicMock()
    mock_session.execute.return_value = mock_result
    mock_result.scalar.return_value= SECOND_SALE_DAO

    with pytest.raises(InvalidStateError)as exc_info:
        await repo.edit_sale_discount(sale_id,discount)
    assert exc_info.value.status==420

    mock_result.scalar.return_value= FOURTH_SALE_DAO
    with pytest.raises(InvalidStateError)as exc_info:
        await repo.edit_sale_discount(sale_id,discount)
    assert exc_info.value.status==420

@pytest.mark.asyncio
async def test_edit_sale_status_pending(repo,mock_session):
    sale_id=1
    new_status='PENDING'

    old_status=NEW_SALE_DAO.status
    mock_result = MagicMock()
    mock_session.execute.return_value = mock_result
    mock_result.scalar.return_value= NEW_SALE_DAO


    result=await repo.edit_sale_status(sale_id,new_status)
    assert result.success
    assert NEW_SALE_DAO.status==new_status
    NEW_SALE_DAO.status=old_status

    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once()
@pytest.mark.asyncio
async def test_edit_sale_status_paid(repo,mock_session):
    sale_id=4
    new_status='PAID'

    old_status=FOURTH_SALE_DAO.status
    mock_result = MagicMock()
    mock_session.execute.return_value = mock_result
    mock_result.scalar.return_value= FOURTH_SALE_DAO


    result=await repo.edit_sale_status(sale_id,new_status)
    assert result.success
    assert FOURTH_SALE_DAO.status==new_status
    FOURTH_SALE_DAO.status=old_status
    
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once()

@pytest.mark.asyncio
async def test_edit_sale_status_invalid_status(repo,mock_session):
    sale_id=4
    new_status='PAID'

    old_status=SECOND_SALE_DAO.status
    mock_result = MagicMock()
    mock_session.execute.return_value = mock_result
    mock_result.scalar.return_value= SECOND_SALE_DAO


    with pytest.raises(InvalidStateError)as exc_info:
        await repo.edit_sale_status(sale_id,new_status)
    assert exc_info.value.status==420
    assert SECOND_SALE_DAO.status==old_status

    old_status=NEW_SALE_DAO.status
    mock_result.scalar.return_value= NEW_SALE_DAO


    with pytest.raises(InvalidStateError)as exc_info:
        await repo.edit_sale_status(sale_id,new_status)
    assert exc_info.value.status==420
    assert NEW_SALE_DAO.status==old_status

    new_status='PENDING'

    mock_result.scalar.return_value= SECOND_SALE_DAO
    old_status=SECOND_SALE_DAO.status

    with pytest.raises(InvalidStateError)as exc_info:
        await repo.edit_sale_status(sale_id,new_status)
    assert exc_info.value.status==420
    assert SECOND_SALE_DAO.status==old_status

    old_status=FOURTH_SALE_DAO.status
    mock_result.scalar.return_value= FOURTH_SALE_DAO


    with pytest.raises(InvalidStateError)as exc_info:
        await repo.edit_sale_status(sale_id,new_status)
    assert exc_info.value.status==420
    assert FOURTH_SALE_DAO.status==old_status