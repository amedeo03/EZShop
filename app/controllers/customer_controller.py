from typing import List, Optional
from app.repositories.customer_repository import CustomerRepository
from app.models.DTO.customer_dto import CustomerDTO,CustomerUpdateDTO
from app.models.DTO.card_dto import CardDTO
from app.services.mapper_service import bool_to_response_dto,customerdao_to_responsedto,carddao_to_responsedto
from app.services.input_validator_service import customer_input,control_id,len_control
from app.models.DTO.boolean_response_dto import BooleanResponseDTO

class CustomerController:
    def __init__(self):
        self.repo = CustomerRepository()

    async def create_customer(self, customer_dto: CustomerDTO) -> CustomerDTO: 
        """Create customer"""
        customer_input(customer_dto)
        card=None
        if customer_dto.card is not None and customer_dto.card.card_id is not None:
            customer_dto.card.card_id=customer_dto.card.card_id.zfill(10)
            created=await self.repo.create_customer(customer_dto.name,customer_dto.card.card_id,customer_dto.card.points)
            if created.cardId is not None: 
                card=await self.repo.get_card_by_id(customer_dto.card.card_id)
        else:
            created=await self.repo.create_customer(customer_dto.name,None,0)
        return customerdao_to_responsedto(created,card)
    
    async def list_customer(self) -> List[CustomerDTO]:
        """Get all customer"""
        daos = await self.repo.list_customer()
        return [customerdao_to_responsedto(dao,dao.card) for dao in daos]
    
    async def get_customer(self, customer_id:str) -> Optional[CustomerDTO]:
        """Get customer by id - throws NotFoundError if not found"""
        control_id([customer_id])
        customer_id=int(customer_id)
        dao = await self.repo.get_customer(customer_id)
        return customerdao_to_responsedto(dao,dao.card) if dao else None

    async def update_customer(self, customer_id: int, customer_dto: CustomerUpdateDTO) -> Optional[CustomerDTO]:
        """Update customer - throws NotFoundError if customer doesn't exist, ConflictError if id card is attached an other customer """
        control_id([customer_id])
        customer_input(customer_dto)
        card=None
        if customer_dto.card is None:
            updated = await self.repo.update_customer_only_name(customer_id, customer_dto.name)
        elif customer_dto.card.card_id=="":
            updated = await self.repo.update_customer(customer_id, customer_dto.name, "", -1)
        else:
            customer_dto.card.card_id=customer_dto.card.card_id.zfill(10)
            updated =await self.repo.update_customer(customer_id, customer_dto.name, customer_dto.card.card_id, customer_dto.card.points)
        if updated is not None and updated.cardId is not None:
            card=await self.repo.get_card_by_id(updated.cardId)
        return customerdao_to_responsedto(updated,card) if updated else None  
    
    async def delete_customer(self, customer_id: str) -> BooleanResponseDTO:
        """Delete customer - throws NotFoundError if not found"""
        control_id([customer_id])
        success=await self.repo.delete_customer(int(customer_id))
        return bool_to_response_dto(success)
    
    #card
    async def create_card(self) -> CardDTO: 
        """Create card"""
        created = await self.repo.create_card()
        return carddao_to_responsedto(created)
    
    async def attach_card(self,customer_id:str, card_id:str)->CustomerDTO:
        """
        Attach a card to customer
        """
        control_id([customer_id,card_id])
        len_control(card_id,10)
        card_id=card_id.zfill(10)
        updated = await self.repo.attach_card(customer_id,card_id)
        return customerdao_to_responsedto(updated,updated.card) if updated else None
     
    async def modify_point(self, card_id: str, points:int) -> CardDTO:
        """modify points"""
        control_id([card_id])
        len_control(card_id,10)
        updated= await self.repo.modify_point(card_id.zfill(10),points)
        return carddao_to_responsedto(updated) if updated else None