from app.models.errors.bad_request import BadRequestError
from app.models.errors.invalid_barcode_format_error import InvalidFormatError
from app.repositories.products_repository import ProductsRepository

from app.models.DTO.sale_dto import SaleDTO
from app.models.DTO.sold_product_dto import SoldProductDTO

class SalesController:
    def __init__(self):
        self.repo = ProductsRepository()
        