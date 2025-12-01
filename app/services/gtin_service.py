def gtin(barcode: str) -> bool:
    """
    GTIN algorithm applied on barcode to check validity.
    """
    barcode = "".join(filter(str.isdigit, barcode))
    last_digit = int(barcode[-1])
    data_digits = barcode[:-1]
    weighted_sum = 0

    for i, char_digit in enumerate(reversed(data_digits)):
        digit = int(char_digit)

        if (i + 1) % 2 != 0:
            weight = 3
        else:
            weight = 1

        weighted_sum += digit * weight

    rest = weighted_sum % 10

    if rest == 0:
        check_digit_calculated = 0
    else:
        check_digit_calculated = 10 - rest
    return check_digit_calculated == last_digit
