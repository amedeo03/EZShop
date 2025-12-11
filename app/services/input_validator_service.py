import re

from app.models.errors.bad_request import BadRequestError
from app.models.errors.invalid_barcode_format_error import InvalidFormatError
from app.services.gtin_service import gtin


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


def validate_discount_rate(discount_rate: float) -> None:
    """
    Validate a discount rate parameter, that needs to be comprised between 1 and 0
    """

    if discount_rate < 0.0 or discount_rate >= 1.0:
        raise BadRequestError("discount_rate parameter needs to be between 0.0 and 1.0")
