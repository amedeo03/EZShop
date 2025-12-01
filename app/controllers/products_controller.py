from typing import List, Optional
from app.repositories.user_repository import UserRepository
from app.repositories.products_repository import ProductsRepository
from app.models.DTO.product_dto import ProductTypeDTO
from app.services.mapper_service import productdao_to_product_type_dto


class ProductsController:
    def __init__(self):
        self.repo = ProductsRepository()

    async def create_product(self, product_dto: ProductTypeDTO) -> ProductTypeDTO: 
        """Create user - throws ConflictError if productCode exists"""
        created = await self.repo.create_product(
            product_dto.description,
            product_dto.productCode,
            product_dto.pricePerUnit,
            product_dto.note,
            product_dto.quantity,
            product_dto.position)
        return productdao_to_product_type_dto(created)

    async def list_products(self) -> List[ProductTypeDTO]:
        """Get all products"""
        daos = await self.repo.list_products()
        return [productdao_to_product_type_dto(dao) for dao in daos]
