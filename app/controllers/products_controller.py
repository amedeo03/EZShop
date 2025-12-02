from typing import List, Optional
from app.repositories.products_repository import ProductsRepository
from app.models.DTO.product_dto import ProductTypeDTO
from app.services.mapper_service import productdao_to_product_type_dto
from app.services.gtin_service import gtin
from app.models.errors.invalid_barcode_format_error import InvalidFormatError


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

    async def get_product(self, product_id: int) -> Optional[ProductTypeDTO]:
        """Get product by id - throws NotFoundError if not found"""
        dao = await self.repo.get_product(product_id)
        return productdao_to_product_type_dto(dao) if dao else None

    async def get_product_by_barcode(self, barcode: str) -> Optional[ProductTypeDTO]:
        """Get product by barcode.
        - Throws: NotFoundError if not found of InvaliFormatError if GTIN verification fails
        """
        gtin_result = gtin(barcode)
        if not gtin_result:
            raise InvalidFormatError("Wrong barcode format (GTIN)")

        dao = await self.repo.get_product_by_barcode(barcode)
        return productdao_to_product_type_dto(dao) if dao else None

    async def get_product_by_description(self, description: str) -> Optional[ProductTypeDTO]:
        """Get product by description.
        """
        daos = await self.repo.get_product_by_description(description)
        return [productdao_to_product_type_dto(dao) for dao in daos]
