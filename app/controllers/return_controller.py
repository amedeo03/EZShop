from typing import List, Optional

from app.models.DTO.boolean_response_dto import BooleanResponseDTO
from app.models.DTO.return_transaction_dto import ReturnTransactionDTO
from app.models.DAO.return_transaction_dao import ReturnTransactionDAO
from app.models.DAO.returned_product_dao import ReturnedProductDAO
from app.models.errors.bad_request import BadRequestError
from app.models.errors.notfound_error import NotFoundError
from app.models.errors.invalid_state_error import InvalidStateError
from app.models.errors.insufficient_quantity_sold_error import InsufficientQuantitySoldError
from app.models.return_status_type import ReturnStatus
from app.repositories.return_repository import ReturnRepository
from app.controllers.products_controller import ProductsController
from app.models.DTO.product_dto import ProductTypeDTO
from app.controllers.sales_controller import SalesController
from app.models.DTO.sale_dto import SaleDTO
from app.models.DTO.sold_product_dto import SoldProductDTO
from app.models.DTO.returned_product_dto import ReturnedProductDTO
from app.repositories.returned_products_repository import ReturnedProductsRepository

from app.services.gtin_service import gtin
from app.services.input_validator_service import (
    validate_field_is_positive,
    validate_field_is_present,
    validate_product_barcode
)
from app.services.mapper_service import return_transaction_dao_to_return_transaction_dto


class ReturnController:
    def __init__(self):
        self.repo = ReturnRepository()
        self.returnedProductRepository = ReturnedProductsRepository()
        self.product_controller = ProductsController()
        self.sales_controller = SalesController()
        

    async def create_return_transaction(self, sale_id: int) -> ReturnTransactionDTO:
        """
        Create a new return transaction.

        - Parameters: return_transaction (ReturnDTO)
        - Returns: ReturnDTO
        """
        sale: SaleDTO = await self.sales_controller.get_sale_by_id(
            sale_id
        )
        if sale_id.status != "PAID":
            raise InvalidStateError("Selected sale status is not 'PAID'")

        new_return_transaction: ReturnTransactionDAO = await self.repo.create_return_transaction(
            sale_id=sale_id
        )
        return return_transaction_dao_to_return_transaction_dto(new_return_transaction)
    
    async def list_returns(self) -> List[ReturnTransactionDTO]:
        """
        List present return transactions.

        - Returns: List of ReturnTransactionDTO
        """

        return_transactions_dao: Optional[List[ReturnTransactionDAO]] = await self.repo.list_returns()
        return_transactions_dto: List[ReturnTransactionDTO] = list()
        
        if not return_transactions_dao:
            raise NotFoundError("Return Transaction not found")
        
        for return_transaction_dao in return_transactions_dao:
            return_transactions_dto.append(return_transaction_dao_to_return_transaction_dto(return_transaction_dao))

        return return_transactions_dto
        
        
    async def get_return_by_id(self, return_id: int) -> ReturnTransactionDTO:
        """
        Returns a Return Transaction given its ID, or NotFound if not present

        - Parameters: return_id as int
        - Returns: ReturnTransactionDTO
        """
        #validate_field_is_positive(sale_id, "product_id")
        return_transaction: ReturnTransactionDAO = await self.repo.get_return_by_id(return_id)
        return return_transaction_dao_to_return_transaction_dto(return_transaction)
    
    async def delete_return(self, return_id: int) -> BooleanResponseDTO:

        return_transaction: ReturnTransactionDTO = await self.get_return_by_id(return_id)
        if return_transaction.status == ReturnStatus.REIMBURSED:
            raise InvalidStateError("Cannot delete a reimbursed return")
        await self.repo.delete_return(return_id)

        return BooleanResponseDTO(success=True)
     
    async def list_returns_for_sale_id(self, sale_id: int) -> List[ReturnTransactionDTO]:
        """
        List present return transactions for a given sale ID.

        - Parameters: sale_id as int
        - Returns: List of ReturnTransactionDTO
        """

        return_transactions_dao: List[ReturnTransactionDAO] = await self.repo.list_returns_for_sale_id(sale_id)
        return [
            return_transaction_dao_to_return_transaction_dto(rt)
            for rt in return_transactions_dao
        ]
    
    async def attach_product_to_return_transaction(
        self, return_id: int, barcode: str, amount: int
    ) -> BooleanResponseDTO:
        """
        Attach a product to a given return transaction.

        - Parameters: return_id as int, barcode as str, amount as int
        - Returns: BooleanResponseDTO
        """
        validate_field_is_positive(return_id, "return_id")
        validate_field_is_present(barcode, "barcode")
        validate_product_barcode(barcode)
        validate_field_is_positive(amount, "amount")

        return_transaction: ReturnTransactionDTO = await self.get_return_by_id(return_id)
        if return_transaction.status != "OPEN":
            raise InvalidStateError("Selected return status is not 'OPEN'")

        product: ProductTypeDTO = await self.product_controller.get_product_by_barcode(
            barcode
        )
        sale: SaleDTO = await self.sales_controller.get_sale_by_id(
            return_transaction.sale_id
        )
        
        for sold_item in sale.lines:
            if sold_item.product_barcode == barcode:
                sold_quantity = sold_item.quantity
                break
        else:
            raise BadRequestError(
                "The product with the given barcode was not sold in the sale associated with this return transaction"
            )

        if sold_quantity - amount < 0:
            raise InsufficientQuantitySoldError(
                "Amount selected is greater than quantity sold in the sale"
            )

        if product.id == None:
            raise BadRequestError("Invalid product")

        returned_item: ReturnedProductDTO = (
            await self.returnedProductRepository.create_returned_product(
                product.id, return_id, product.barcode, amount, product.price_per_unit
            )
        )

        return (
            BooleanResponseDTO(success=True)
            if returned_item
            else BooleanResponseDTO(success=False)
        )