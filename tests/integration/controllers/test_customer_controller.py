from datetime import datetime
from unittest.mock import AsyncMock

import pytest
import pytest_asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.controllers.customer_controller import CustomerController
from app.models.DTO.customer_dto import CustomerDTO, CustomerUpdateDTO

from app.models.errors.conflict_error import ConflictError
from app.models.errors.customer_card_error import CustomerCardError
from app.repositories.customer_repository import CustomerRepository
from app.database.database import Base
from app.models.DAO.customer_dao import CustomerDAO
from app.models.DAO.card_dao import CardDAO
from app.models.DTO.card_dto import CardDTO
from app.models.errors.app_error import AppError
from app.models.errors.bad_request import BadRequestError
from app.models.errors.balance_error import BalanceError
from app.models.errors.notfound_error import NotFoundError
from app.repositories.orders_repository import OrdersRepository


DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture
async def db_session():
    engine = create_async_engine(DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    SessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)

    async with SessionLocal() as session:
        yield session

    await engine.dispose()


@pytest.mark.asyncio
class TestCustomerController:

    @pytest.mark.parametrize(
        "new_customer, expected_exception",
        [
            (  # Success
                CustomerDAO(
                    name="John Doe", cardId=None
                ),
                None,
            ),
            (  # Empty name
                CustomerDAO(
                    name="", cardId=None
                ),
                BadRequestError,
            ),
        ],
    )
    async def test_create_customer(
        self, db_session, new_customer, expected_exception
    ):
        repo = CustomerRepository(session=db_session)
        controller = CustomerController()
        controller.repo = repo
        
        if expected_exception:
            with pytest.raises(expected_exception):
                await controller.create_customer(new_customer)

            db_result = await db_session.execute(
                select(CustomerDAO).where(
                    CustomerDAO.name == new_customer.name
                )
            )
            assert db_result.scalars().first() is None
        else:
            await controller.create_customer(new_customer)

            db_result = await db_session.execute(
                select(CustomerDAO).where(
                    CustomerDAO.name == new_customer.name
                )
            )
            saved_customer = db_result.scalars().first()
            assert saved_customer is not None
            assert saved_customer.name == new_customer.name
            assert isinstance(saved_customer.id, int)
            
            
    @pytest.mark.asyncio
    async def test_list_customers(self, db_session):
        repo = CustomerRepository(session=db_session)
        controller = CustomerController()
        controller.repo = repo

        customer1 = CustomerDAO(
            name="John Doe", cardId=None
        )
        customer2 = CustomerDAO(
            name="Jane Smith", cardId=None
        )
        db_session.add_all([customer1, customer2])
        await db_session.commit()

        customers = await controller.list_customer()

        assert len(customers) == 2
        assert isinstance(customers[0], CustomerDTO)
        assert customers[0].name == "John Doe"
        assert customers[1].name == "Jane Smith"
           
        

    @pytest.mark.parametrize(
        "customer, customer_id, expected_exception",
        [
            (  # Success
                CustomerDAO(
                    name="John Doe", cardId=None
                ),
                "1",
                None,
            ),
            (  # Invalid ID -> negative ID
                CustomerDAO(
                    name="John Doe", cardId=None
                ),
                "-1",
                BadRequestError,
            ),
            (  # Invalid ID -> empty ID
                CustomerDAO(
                    name="John Doe", cardId=None
                ),
                "",
                BadRequestError,
            ),
            (  # Inavlaid ID -> Int
                CustomerDAO(
                    name="John Doe", cardId=None
                ),
                1,
                AttributeError,
            ),
            (  # Invalaid ID -> String
             CustomerDAO(
                    name="John Doe", cardId=None
                ),
                "abc",
                BadRequestError,
            ),
            (  # Invalaid ID -> String
             CustomerDAO(
                    name="John Doe", cardId=None
                ),
                "999",
                NotFoundError,
            ),
        ],
    )
    async def test_get_customer_by_id(
        self, db_session, customer, customer_id, expected_exception
    ):
        
        repo = CustomerRepository(session=db_session)
        controller = CustomerController()
        controller.repo = repo
        await controller.create_customer(customer)
        
        if expected_exception:
            with pytest.raises(expected_exception):
                await controller.get_customer(customer_id)
        else:

            customer_dto = await controller.get_customer(customer_id)

            assert customer_dto is not None
            assert customer_dto.id == int(customer_id)
            assert isinstance(customer_dto, CustomerDTO)
            
    # --- TEST CARD FUNCTIONS ---
    
    # --- Create Card ---
    
    async def test_create_card(
        self, db_session
    ):
        repo = CustomerRepository(session=db_session)
        controller = CustomerController()
        controller.repo = repo
        
        card = await controller.create_card()

        db_result = await db_session.execute(
            select(CardDAO).where(
                CardDAO.cardId == card.card_id
            )
        )
        saved_card = db_result.scalars().first()
        
        assert saved_card is not None
        assert saved_card.cardId.isdigit() and len(saved_card.cardId) == 10
        assert saved_card.points == 0
        assert isinstance(saved_card, CardDAO)

    # --- Test Attach Card to a Customer ---

    @pytest.mark.parametrize(
        "new_customer, new_customer_id, new_customer_2, new_card, card_id, expected_exception",
        [
            (  # Success
                CustomerDAO(
                    id=1, name="John Doe", cardId=None
                ),
                "1",
                CustomerDAO(
                    id=2, name="Jane Smith", cardId=None
                ),
                CardDAO(
                    cardId="0000000001", points=0
                ),
                "0000000001",
                None,
            ),
            (  # Card is already attached to a different Customer
                CustomerDAO(
                    id= 1, name="John Doe", cardId=None
                ),
                "1",
                CustomerDAO(
                    id=2, name="Jane Smith", cardId="0000000001"
                ),
                CardDAO(
                    cardId="0000000001", points=0
                ),
                "0000000001",
                ConflictError,
            ),
            (  # Card ID is not an "Integer String"
                CustomerDAO(
                    id=1, name="John Doe", cardId=None
                ),
                "1",
                CustomerDAO(
                    id=2, name="Jane Smith", cardId="0000000001"
                ),
                CardDAO(
                    cardId="abc", points=0
                ),
                "abc",
                BadRequestError,
            ),
            (  # Card ID is empty
                CustomerDAO(
                    id=1, name="John Doe", cardId=None
                ),
                "1",
                CustomerDAO(
                    id=2, name="Jane Smith", cardId="0000000001"
                ),
                CardDAO(
                    cardId="abc", points=0
                ),
                "",
                BadRequestError,
            ),
            (  # Customer ID is empty
                CustomerDAO(
                    id=1, name="John Doe", cardId=None
                ),
                "",
                CustomerDAO(
                    id=2, name="Jane Smith", cardId="0000000001"
                ),
                CardDAO(
                    cardId="0000000001", points=0
                ),
                "0000000001",
                BadRequestError,
            ),
            (  # Customer does not exists
                CustomerDAO(
                    id=1, name="John Doe", cardId=None
                ),
                "999",
                CustomerDAO(
                    id=2, name="Jane Smith", cardId="0000000001"
                ),
                CardDAO(
                    cardId="abc", points=0
                ),
                "0000000001",
                NotFoundError,
            ),
            (  # Card does not exists
                CustomerDAO(
                    id=1, name="John Doe", cardId=None
                ),
                "999",
                CustomerDAO(
                    id=2, name="Jane Smith", cardId="0000000001"
                ),
                CardDAO(
                    cardId="abc", points=0
                ),
                "0000000999",
                NotFoundError,
            ),
        ],
    )
    async def test_attach_card(
        self, db_session, new_customer, new_customer_id, new_customer_2, new_card, card_id, expected_exception
    ):
        repo = CustomerRepository(session=db_session)
        controller = CustomerController()
        controller.repo = repo

        db_session.add_all([new_customer, new_customer_2, new_card])
        await db_session.commit()
        
        if expected_exception:
            with pytest.raises(expected_exception):
                await controller.attach_card(customer_id=new_customer_id, card_id=card_id)

            db_result = await db_session.execute(
                select(CustomerDAO).where(
                    CustomerDAO.id == new_customer.id
                )
            )
            customer = db_result.scalars().first()
            
            assert customer.cardId != new_card.cardId
        else:
            await controller.attach_card(customer_id=new_customer_id, card_id=card_id)

            db_result = await db_session.execute(
                select(CustomerDAO).where(
                    CustomerDAO.id == new_customer.id
                )
            )
            # check if the customer has the card attached
            saved_customer = db_result.scalars().first()
            assert saved_customer is not None
            assert saved_customer.cardId == new_card.cardId

         
    @pytest.mark.parametrize(
        "card, card_id, points, expected_exception",
        [
            (  # Success
                CardDAO(
                    cardId="0000000001", points=0
                ),
                "0000000001",
                120,
                None,
            ),  
            (  # Success points + new points
                CardDAO(
                    cardId="0000000001", points=100
                ),
                "0000000001",
                120,
                None,
            ), 
            (  # Insufificient Points
                CardDAO(
                    cardId="0000000001", points=100
                ),
                "0000000001",
                -120,
                CustomerCardError,
            ),  
            (  # Invalid Card ID
                CardDAO(
                    cardId="0000000001", points=100
                ),
                "abc",
                100,
                BadRequestError,
            ),  
            (  # Card Not Found
                CardDAO(
                    cardId="0000000001", points=100
                ),
                "0000000002",
                120,
                NotFoundError,
            ),  
            (  # Empty Card ID
                CardDAO(
                    cardId="0000000001", points=100
                ),
                "",
                120,
                BadRequestError,
            ),  
            (  # Empty points
                CardDAO(
                    cardId="0000000001", points=100
                ),
                "0000000001",
                "",
                BadRequestError,
            ),  
        ],
    )
    async def test_modify_point(
        self, db_session, card, card_id, points, expected_exception
    ):
        repo = CustomerRepository(session=db_session)
        controller = CustomerController()
        controller.repo = repo

        card_points_before = card.points
        
        db_session.add_all([card])
        await db_session.commit()
        
        if expected_exception:
            with pytest.raises(expected_exception):
                await controller.modify_point(card_id=card_id, points=points)

            db_result = await db_session.execute(
                select(CardDAO).where(
                    CardDAO.cardId == card_id
                )
            )
            saved_card = db_result.scalars().first()
            # check if the customer has the card attached
            if saved_card is not None:            
                assert saved_card.points == card_points_before
        else:
            await controller.modify_point(card_id=card_id, points=points)

            db_result = await db_session.execute(
                select(CardDAO).where(
                    CardDAO.cardId == card_id
                )
            )
            # check if the customer has the card attached
            saved_card = db_result.scalars().first()
            assert saved_card is not None
            assert saved_card.points == card_points_before + points   
            
    
    @pytest.mark.parametrize(
        "customer, customer_id,  expected_exception",
        [
            (  # Success
                CustomerDAO(
                    id=1, name="John Doe", cardId=None
                ),
                "1",
                None,
            ),
            (  # NotFoundError
                CustomerDAO(
                    id=1, name="John Doe", cardId=None
                ),
                "999",
                NotFoundError,
            ),  
        ]
    )
    
    async def test_delete_customer(
        self, db_session, customer, customer_id, expected_exception
    ):
        repo = CustomerRepository(session=db_session)
        controller = CustomerController()
        controller.repo = repo

        
        db_session.add_all([customer])
        await db_session.commit()
        
        if expected_exception:
            with pytest.raises(expected_exception):
                await controller.delete_customer(customer_id=customer_id)

        else:
            await controller.delete_customer(customer_id=customer_id)

            db_result = await db_session.execute(
                select(CustomerDAO).where(
                    CustomerDAO.id == customer_id
                )
            )
            # check if the customer has been deleted
            assert db_result.scalars().first() is None
 
            
    @pytest.mark.parametrize(
        "customer, customer_id, updated_customer, card, expected_exception",
        [
            (  # Update ONLY Name Success
                CustomerDAO(
                   id= 1, name="John Doe", cardId="0000000001"
                ),
                '1',
                CustomerUpdateDTO(
                    id= 1, name="John Updated"),
                CardDAO(
                    cardId="0000000001", points=0),
                None,
            ),
            (  # Customer Not Found
                CustomerDAO(
                   id= 1, name="John Doe", cardId="0000000001"
                ),
                '999',
                CustomerUpdateDTO(
                    id= 1, name="John Updated"),
                CardDAO(
                    cardId="0000000001", points=0),
                NotFoundError,
            ),
            (  # Empty Customer ID
                CustomerDAO(
                   id= 1, name="John Doe", cardId="0000000001"
                ),
                '',
                CustomerUpdateDTO(
                    id= 1, name="John Updated"),
                CardDAO(
                    cardId="0000000001", points=0),
                BadRequestError,
            ),
            (  # Update Card Number -> Success
                CustomerDAO(
                   id= 1, name="John Doe", cardId="0000000001"
                ),
                "1",
                CustomerUpdateDTO(
                    id= 1, name="John Doe", card= {
                                                    "card_id": "0000000002",
                                                    "points": 0
                                                }),
                CardDAO(
                    cardId="0000000002", points=0),
                None,
            ),
            (  # Update Card Number -> Card ID not found
                CustomerDAO(
                   id= 1, name="John Doe", cardId="0000000001"
                ),
                "1",
                CustomerUpdateDTO(
                    id= 1, name="John Doe", card= {
                                                    "card_id": "0000000099",
                                                    "points": 0
                                                }),
                CardDAO(
                    cardId="0000000002", points=0),
                NotFoundError,
            ),
        ],
    )
    async def test_update_customer(
        self, db_session, customer, customer_id, updated_customer, card, expected_exception
    ):
        
        repo = CustomerRepository(session=db_session)
        controller = CustomerController()
        controller.repo = repo
        
        db_session.add_all([customer, card])
        await db_session.commit()
           
        if expected_exception:
            with pytest.raises(expected_exception):
                await controller.update_customer(customer_id, updated_customer)
                
            db_result = await db_session.execute(
                select(CustomerDAO).where(
                    CustomerDAO.id == customer_id
                )
            )
            if expected_exception == BadRequestError:
                assert db_result.scalars().first() is None
                
        else:
            await controller.update_customer(customer_id, updated_customer)

            db_result = await db_session.execute(
                select(CustomerDAO).where(
                    CustomerDAO.id == customer_id
                )
            )
            saved_updated_customer = db_result.scalars().first()

            assert saved_updated_customer is not None
            assert saved_updated_customer.name == updated_customer.name
            
            if updated_customer.card is not None:
                assert saved_updated_customer.cardId == updated_customer.card.card_id
  
    @pytest.mark.parametrize(
        "customer, customer_id, updated_customer, card, expected_exception",
        [
            (  # Detach Customer Card and delete Card Success
                CustomerDAO(
                   id= 1, name="John Doe", cardId="0000000001"
                ),
                "1",
                CustomerUpdateDTO(
                    name="John Doe", card={
                                            "card_id": "",
                                            "points": 0
                                        }),
                CardDAO(
                    cardId="0000000001", points=0),
                None,
            ),
            
        ],
    )
    async def test_update_customer_detach_card(
        self, db_session, customer, customer_id, updated_customer, card, expected_exception
    ):
        
        repo = CustomerRepository(session=db_session)
        controller = CustomerController()
        controller.repo = repo
        
        db_session.add_all([customer, card])
        await db_session.commit()
           
        await controller.update_customer(customer_id, updated_customer)

        db_result = await db_session.execute(
            select(CustomerDAO).where(
                CustomerDAO.id == customer_id
            )
        )
        
        db_result_card = await db_session.execute(
            select(CardDAO).where(
                CardDAO.cardId == customer.cardId
            )
        )
        saved_updated_customer = db_result.scalars().first()

        assert saved_updated_customer.cardId == None
        assert db_result_card.scalars().first() is None

  

    @pytest.mark.parametrize(
        "customer_1, customer_2, updated_customer_1, card, expected_exception",
        [
            (  # Detach Customer Card and delete Card Success
                CustomerDAO(
                   id=1, name="John Doe", cardId=None
                ),
                CustomerDAO(
                   id=2, name="Jane Smith", cardId="0000000001"
                ),
                CustomerUpdateDTO(
                    name="John Doe", card={
                                            "card_id": "0000000001",
                                            "points": 0
                                        }),
                CardDAO(
                    cardId="0000000001", points=0),
                ConflictError,
            ),
            
        ],
    )
    async def test_update_customer_with_card_already_attached(
        self, db_session, customer_1, customer_2, updated_customer_1, card, expected_exception
    ):
        
        repo = CustomerRepository(session=db_session)
        controller = CustomerController()
        controller.repo = repo
        
        db_session.add_all([customer_1, customer_2, card])
        await db_session.commit()
        
        if expected_exception:
            with pytest.raises(expected_exception):
                await controller.update_customer(str(customer_1.id), updated_customer_1)

        db_result = await db_session.execute(
            select(CustomerDAO).where(
                CustomerDAO.id == customer_1.id
            )
        )
        saved_updated_customer = db_result.scalars().first()

        # customer 1 should still have no card attached
        assert saved_updated_customer.cardId == None

  
