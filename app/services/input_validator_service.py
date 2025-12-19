import re

from app.models.errors.bad_request import BadRequestError
from app.models.errors.invalid_barcode_format_error import InvalidFormatError
from app.services.gtin_service import gtin
from app.models.DTO.customer_dto import CustomerCreateDTO,CustomerUpdateDTO,CustomerDTO


def validate_id(id: int):
    if id < 0:
        raise BadRequestError("'id' must be positive")


def validate_product_barcode(barcode: str) -> None:
    """
    Validate product barcode (String length + GTIN algorithm).
    - Parameters: barcode (str)
    - Throws:
        - BadRequestError if barcode is not a string of 12-14 digits
        - InvalidFormatError if GTIN check fails
    """
    if len(barcode) < 12 or len(barcode) > 14:
        raise BadRequestError("productCode must be a string of 12-14 digits")
    elif not gtin(barcode):
        raise InvalidFormatError("Wrong barcode format (GTIN)")


def validate_field_is_present(field: str, field_name: str) -> None:
    """
    Checks if a filed is present (None or empty field).
    - Parameteres: field (str), field_name (str)
    - Throws:
        - BadRequestError if field is not present
    """
    if field is None or field == "":
        raise BadRequestError(f"'{field_name}' is a mandatory field")


def validate_field_is_positive(field: float, field_name: str) -> None:
    """
    Checks if 'field' is positive (>=0).
    - Parameters: field (float), field_name (str)
    - Throws:
        - BadRequestError if field is negative.
    """
    if field <= 0:
        raise BadRequestError(f"'{field_name}' must be positive")


def validate_product_position(position: str) -> None:
    """
    Validate the pattern of the position of a product
    - Parameters: position (str)
    - Throws:
        - BadRequestError if position doesn't match the pattern 'aisle-shelf-level'
    """
    position_pattern = re.compile(r"^\w-\w-\w$")

    if position == "":
        return

    if not position_pattern.match(position):
        raise BadRequestError(
            "'position' pattern must be 'aisle-shelf-level' or empty string to clear it."
        )

def customer_input(customer: CustomerCreateDTO|CustomerUpdateDTO|CustomerDTO) ->None:
    if not customer.name:
        raise BadRequestError("Customer name is required")
    
def control_id(id: list[str]):
    for i in id:
        if not(i.isdigit()):
            raise BadRequestError("Invalid ID")

def len_control(id: str, l: int):
    if len(id)>l:
        raise BadRequestError("Invalid card ID")
