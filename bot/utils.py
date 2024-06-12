import math


def set_significant_digits(value, digits):
    """
    Set the significant digits of a float to the specified number, rounding down if necessary.

    :param value: The float value to adjust.
    :param digits: The number of significant digits.
    :return: The adjusted float value.
    """
    if digits <= 0:
        raise ValueError("Number of significant digits must be positive.")

    if value == 0:
        return 0.0

    # Determine the exponent of the value
    exponent = math.floor(math.log10(abs(value)))

    # Calculate the factor to scale the value
    factor = 10 ** (digits - 1 - exponent)

    # Adjust the value to the desired significant digits
    adjusted_value = math.floor(value * factor) / factor

    return adjusted_value
