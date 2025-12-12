from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select ,func
from app.models.DAO.customer_dao import CustomerDAO
from app.models.DAO.card_dao import CardDAO
from app.models.errors.bad_request import BadRequestError
from app.models.errors.notfound_error import NotFoundError
from app.models.errors.customer_card_error import CustomerCardError
from app.database.database import AsyncSessionLocal
from typing import Optional
from sqlalchemy.orm import selectinload
from app.models.errors.conflict_error import ConflictError
from app.utils import find_or_throw_not_found, throw_conflict_if_found



class CustomerRepository:

    def __init__(self, session: Optional[AsyncSession] = None):
        self._session = session

    async def _get_session(self) -> AsyncSession:
        return self._session or AsyncSessionLocal()

    async def create_customer(self, name: str,cardId: str, points: int) -> CustomerDAO:
        """
        Create customer
        """
        
        async with await self._get_session() as session:
            card=await self.get_card_by_id(cardId)
            if   card is None:
                customer = CustomerDAO(name=name, cardId=None)
            else:
                result_conflict = await session.execute(select(CustomerDAO).filter(CustomerDAO.cardId == cardId))
                result_conflict=result_conflict.scalars().first()
                if result_conflict is None:
                    customer = CustomerDAO(name=name, cardId=cardId)
                    card=  await session.get(CardDAO, cardId)
                    if(card.points!=points):
                        card.points= points
                else:
                    customer = CustomerDAO(name=name, cardId=None)
            session.add(customer)
            await session.commit()
            await session.refresh(customer,attribute_names=["card"])
            return customer
        
    async def list_customer(self) -> list[CustomerDAO]:
        """Get all customer"""
        async with await self._get_session() as session:
            result = await session.execute(select(CustomerDAO).options(selectinload(CustomerDAO.card)))
            return result.scalars().all()
        
    async def get_customer(self, customer_id: int) -> CustomerDAO | None:
        """
        Get customer by id or throw NotFoundError if not found
        """
        async with await self._get_session() as session:
            customer = await session.execute(
                    select(CustomerDAO)
                    .options(selectinload(CustomerDAO.card))
                    .filter(CustomerDAO.id==customer_id))
            customer= customer.scalars().first()
            return find_or_throw_not_found(
                [customer] if customer else [],
                lambda _: True,
                f"Customer with id '{customer_id}' not found"
            )
    
    async def update_customer_only_name(self, customer_id: int, updated_name: str) -> CustomerDAO | None:
        """
        Update customer information. Throw NotFoundError if not found or ConflictError if the new username exists
        """
        async with await self._get_session() as session:
            db_customer = await session.get(CustomerDAO, customer_id)
            if not db_customer:
                return None

            db_customer.name = updated_name

            await session.commit()
            await session.refresh(db_customer)
            return db_customer

    async def update_customer(self, customer_id: int, updated_name: str, updated_cardId: str, updated_points:int) -> CustomerDAO | None:
        """
        Update customer information. Throw NotFoundError if not found or ConflictError if the new username exists
        """
        async with await self._get_session() as session:
            db_customer = await session.get(CustomerDAO, customer_id)
            if not db_customer:
                return None
            db_customer.name=updated_name
            if(updated_cardId==""and updated_points==-1):
                db_card = await session.get(CardDAO, db_customer.cardId)
                db_customer.cardId=None
                if db_card is not None:
                    await session.delete(db_card)
            else:
                db_card = await session.get(CardDAO, updated_cardId)
                if db_card is None:
                    raise NotFoundError("Card not found")
                result_conflict = await session.execute(select(CustomerDAO).filter(CustomerDAO.cardId == updated_cardId))
                result_conflict=result_conflict.scalars().first()
                if not(result_conflict is None or result_conflict.id==customer_id):
                    raise ConflictError("Card with id "+updated_cardId+" is already attached to a customer")
                db_customer.cardId=updated_cardId
                db_card.points=updated_points

            await session.commit()
            await session.refresh(db_customer,attribute_names=["card"])
            return db_customer
        
    async def delete_customer(self, customer_id: int) -> bool:
        """
        Delete customer by id. Will throw NotFoundError if customer doesn't exist
        """
        async with await self._get_session() as session:
            customer = await session.get(CustomerDAO, customer_id)

            find_or_throw_not_found(
                [customer] if customer else [],
                lambda _: True,
                f"customer with id '{customer_id}' not found"
            )

            await session.delete(customer)
            await session.commit()
            return True
#card
    async def create_card(self, cardId: str) -> CardDAO:
        """
        Create card
        """
        
        async with await self._get_session() as session:
            id_db= await session.execute(select(CardDAO).order_by(CardDAO.cardId))
            id_db= id_db.scalars().first()
            id=int(id_db.cardId)
            id=id+1
            id=str(id).zfill(10)
            card= CardDAO(cardId=id,points=0)
            session.add(card)
            await session.commit()
            await session.refresh(card)
            return card
    
    async def attach_card(self, customer_id: str, card_id: str)-> CustomerDAO:
        "attach card"
        async with await self._get_session() as session:
            card=await session.get(CardDAO,card_id)
            customer=await session.execute(select(CustomerDAO).filter(customer_id==CustomerDAO.id))
            customer=customer.scalars().first()
            result_conflict = await session.execute(select(CustomerDAO).filter(CustomerDAO.cardId == card_id))
            result_conflict=result_conflict.scalars().first()
            if card is None or customer is None:
                return None
            if result_conflict is not None:
                print(result_conflict)
                raise ConflictError("Card with id "+card_id+" is already attached to a customer")
            customer.cardId=card_id
            await session.commit()
            await session.refresh(customer, attribute_names=["card"])
            return customer
        
    async def modify_point(self, cardId: str,points: int) -> CardDAO:
        """update point"""
        async with await self._get_session() as session:
            card= await session.get(CardDAO,cardId)
            if card is None:
                return None
            if card.points+points<0:
                raise CustomerCardError("Insufficient points on the card")
            card.points+=points
            await session.commit()
            await session.refresh(card)
            return card

    async def get_card_by_id(self, cardId:str)->CardDAO|None:
        """get card by id"""
        async with await self._get_session() as session:
            card= await session.get(CardDAO,cardId)
            if card is None or cardId is None:
                return None
            return card
