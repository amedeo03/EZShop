from typing import List, Optional
from app.repositories.customer_repository import CustomerRepository
from app.models.DTO.customer_dto import CustomerDTO
from app.models.DTO.card_dto import CardDTO
from app.services.mapper_service import bool_to_response_dto,customerdao_to_responsedto,carddao_to_responsedto
from app.services.input_validator_service import custumer_input,validate_id
from app.models.errors.bad_request import BadRequestError
from app.models.errors.notfound_error import NotFoundError
from app.models.DTO.boolean_response_dto import BooleanResponseDTO

class CustomerController:
    def __init__(self):
        self.repo = CustomerRepository()

    async def create_customer(self, customer_dto: CustomerDTO) -> CustomerDTO: 
        """Create customer"""
        custumer_input(customer_dto)
        if customer_dto.card is not None:
            created=await self.repo.create_customer(customer_dto.name,customer_dto.card.cardId,customer_dto.card.points)
            card=await self.repo.get_card_by_id(customer_dto.card.cardId)
        else:
            created=await self.repo.create_customer(customer_dto.name,None,0)
            card=None
        return customerdao_to_responsedto(created,card)
    
    async def list_customer(self) -> List[CustomerDTO]:
        """Get all customer"""
        daos = await self.repo.list_customer()
        return [customerdao_to_responsedto(dao,dao.card) for dao in daos]
    
    async def get_customer(self, customer_id:str) -> Optional[CustomerDTO]:
        """Get customer by id - throws NotFoundError if not found"""
        if not(customer_id.isdigit()):
            raise BadRequestError("Invalid customer ID")
        customer_id=int(customer_id)
        dao = await self.repo.get_customer(customer_id)
        return customerdao_to_responsedto(dao,dao.card) if dao else None

    async def update_customer(self, customer_id: int, customer_dto: CustomerDTO) -> Optional[CustomerDTO]:
        """Update customer - throws NotFoundError if customer doesn't exist, ConflictError if id card is attached an other customer """
        card=None
        if customer_dto.card is None:
            updated = await self.repo.update_customer_only_name(customer_id, customer_dto.name)
        elif customer_dto.card.points ==0 and customer_dto.card.cardId is None:
            updated = await self.repo.update_customer(customer_id, customer_dto.name, "", -1)
        else:
            updated =await self.repo.update_customer(customer_id, customer_dto.name, customer_dto.card.cardId, customer_dto.card.points)
        if updated.cardId is not None:
            card=await self.repo.get_card_by_id(updated.cardId)
        return customerdao_to_responsedto(updated,card) if updated else None  
    
    async def delete_customer(self, customer_id: str) -> BooleanResponseDTO:
        """Delete customer - throws NotFoundError if not found"""
        if not (customer_id.isdigit()):
            raise BadRequestError("Invalid customer ID")
        success=await self.repo.delete_customer(int(customer_id))
        return bool_to_response_dto(success)
    
    #card
    card_id="0000000000"
    async def create_card(self) -> CardDTO: 
        """Create card"""
        id=int(self.card_id)
        id=id+1
        self.card_id=str(id).zfill(10)
        created = await self.repo.create_card(self.card_id)
        return carddao_to_responsedto(created)
    
    async def attach_card(self,customer_id:str, card_id:str)->CustomerDTO:
        """
        Attach a card to customer
        """
        updated = await self.repo.attach_card(customer_id,card_id)
        return customerdao_to_responsedto(updated,updated.card) if updated else None
     
    async def modify_point(self, card_id: str,points:int) -> CardDTO:
        """modify points"""
        updated= await self.repo.modify_point(card_id,points)
        return carddao_to_responsedto(updated) if updated else None