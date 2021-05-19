# type annotation prevents float, None, etc
def calc_subnet_mask(cidr_number: int) -> str:
    """Calculates the correct submask from the given number in CIDR notation"""
    if not 0 <= cidr_number <= 32:  # checking if value is in expected range
        raise ValueError(
            "CIDR values are between 0 and 32 inclusive, received {}".format(
                str(cidr_number),
            )
        )

    bit_string = ("1" * cidr_number).ljust(32, "0")
    byte_strings = [bit_string[i:i + 8] for i in range(0, len(bit_string), 8)]
    byte_list = [str(int(y, 2)) for y in byte_strings]
    return ".".join(byte_list)
