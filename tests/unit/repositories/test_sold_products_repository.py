
from unittest.mock import AsyncMock, MagicMock
import pytest

from app.models.DAO.sale_dao import SaleDAO
from app.models.DAO.sold_product_dao import SoldProductDAO
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
    return SoldProductsRepository(session=mock_session)

@pytest.mark.asyncio
async def test_create_sold_product_ok(repo, mock_session):
    
    mock_result=MagicMock()
    mock_result.scalar_one_or_none.return_value=None
    mock_session.execute.return_value = mock_result

    result=await repo.create_sold_product(
        FIRST_PRODUCT_DAO.id,
        FIRST_PRODUCT_DAO.sale_id,
        FIRST_PRODUCT_DAO.product_barcode,
        FIRST_PRODUCT_DAO.quantity,
        FIRST_PRODUCT_DAO.price_per_unit,
        FIRST_PRODUCT_DAO.discount_rate,
    )
    assert isinstance(result,SoldProductDAO)
    assert FIRST_PRODUCT_DAO.id==result.id
    assert FIRST_PRODUCT_DAO.sale_id==result.sale_id
    assert FIRST_PRODUCT_DAO.product_barcode==result.product_barcode
    assert FIRST_PRODUCT_DAO.quantity==result.quantity
    assert FIRST_PRODUCT_DAO.price_per_unit==result.price_per_unit
    assert FIRST_PRODUCT_DAO.discount_rate==result.discount_rate

    mock_session.add.assert_called_once()
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once()

@pytest.mark.asyncio
async def test_create_sold_product_conflict(repo, mock_session):
    
    mock_result=MagicMock()
    mock_result.scalar_one_or_none.return_value=FIRST_PRODUCT_DAO
    mock_session.execute.return_value = mock_result
    with pytest.raises(ConflictError)as exc_info:
        await repo.create_sold_product(
            FIRST_PRODUCT_DAO.id,
            FIRST_PRODUCT_DAO.sale_id,
            FIRST_PRODUCT_DAO.product_barcode,
            FIRST_PRODUCT_DAO.quantity,
            FIRST_PRODUCT_DAO.price_per_unit,
            FIRST_PRODUCT_DAO.discount_rate,
        )
    assert exc_info.value.status==409

@pytest.mark.asyncio
async def test_get_sold_product_by_id_ok(repo, mock_session):
    product_id=1

    mock_result=MagicMock()
    mock_result.scalars.return_value.all.return_value = [FIRST_PRODUCT_DAO]
    mock_session.execute.return_value = mock_result

    result=await repo.get_sold_product_by_id(product_id)
    assert isinstance(result,list)
    result=result[0]
    assert FIRST_PRODUCT_DAO.id==result.id
    assert FIRST_PRODUCT_DAO.sale_id==result.sale_id
    assert FIRST_PRODUCT_DAO.product_barcode==result.product_barcode
    assert FIRST_PRODUCT_DAO.quantity==result.quantity
    assert FIRST_PRODUCT_DAO.price_per_unit==result.price_per_unit
    assert FIRST_PRODUCT_DAO.discount_rate==result.discount_rate
    mock_session.execute.assert_called_once()

@pytest.mark.asyncio
async def test_get_sold_product_by_id_not_found(repo, mock_session):
    product_id=1

    #mock_result.scalars.return_value.all.return_value = []
    mock_session.execute.return_value = None

    with pytest.raises(NotFoundError)as exc_info:
        await repo.get_sold_product_by_id(product_id)
    exc_info.value.status==404

@pytest.mark.asyncio
async def test_edit_quantity_ok(repo, mock_session):
    id=1 
    sale_id=1 
    quantity=1

    old_quantity=FIRST_PRODUCT_DAO.quantity
    
    mock_result=MagicMock()
    mock_result.scalar.return_value= FIRST_PRODUCT_DAO
    mock_session.execute.return_value = mock_result

    result=await repo.edit_sold_product_quantity(id, sale_id,quantity)
    
    assert result.success
    assert FIRST_PRODUCT_DAO.quantity==(old_quantity+quantity)
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once()

    result=await repo.edit_sold_product_quantity(id, sale_id,-quantity)
    assert result.success
    assert FIRST_PRODUCT_DAO.quantity==(old_quantity+quantity-quantity)

    FIRST_PRODUCT_DAO.quantity=old_quantity


@pytest.mark.asyncio
async def test_edit_quantity_not_found(repo, mock_session):
    id=1 
    sale_id=1 
    quantity=1

    #mock_result.scalars.return_value.all.return_value = []
    mock_session.execute.return_value = None

    with pytest.raises(NotFoundError)as exc_info:
        await repo.edit_sold_product_quantity(id, sale_id,quantity)
    assert exc_info.value.status==404

@pytest.mark.asyncio
async def test_edit_quantity_big_quantity(repo, mock_session):
    id=1 
    sale_id=1 
    quantity=-1000
    old_quantity=FIRST_PRODUCT_DAO.quantity

    mock_result=MagicMock()
    mock_result.scalar.return_value= FIRST_PRODUCT_DAO
    mock_session.execute.return_value = mock_result

    with pytest.raises(BadRequestError)as exc_info:
        await repo.edit_sold_product_quantity(id, sale_id,quantity)
    assert exc_info.value.status==400
    assert old_quantity==FIRST_PRODUCT_DAO.quantity

@pytest.mark.asyncio
async def test_edit_discount_ok(repo, mock_session):
    id=1,
    sale_id=1
    discount=0.5
    old_discount=FIRST_PRODUCT_DAO.discount_rate
    
    mock_result=MagicMock()
    mock_result.scalar.return_value= FIRST_PRODUCT_DAO
    mock_session.execute.return_value = mock_result

    result=await repo.edit_sold_product_discount(id,sale_id,discount)
    
    assert result.success
    assert FIRST_PRODUCT_DAO.discount_rate==discount
    FIRST_PRODUCT_DAO.discount_rate=old_discount

@pytest.mark.asyncio
async def test_edit_discount_not_found(repo, mock_session):
    id=1 
    sale_id=1 
    discount=1

    #mock_result.scalars.return_value.all.return_value = []
    mock_session.execute.return_value = None

    with pytest.raises(NotFoundError)as exc_info:
        await repo.edit_sold_product_discount(id, sale_id,discount)
    assert exc_info.value.status==404

@pytest.mark.asyncio
async def test_remove_ok(repo, mock_session):
    id=1,
    sale_id=2,
    barcode=FIRST_PRODUCT_DAO.product_barcode

    mock_result=MagicMock()
    mock_result.scalar.return_value= FIRST_PRODUCT_DAO
    mock_session.execute.return_value = mock_result

    await repo.remove_sold_product(id,sale_id,barcode)
