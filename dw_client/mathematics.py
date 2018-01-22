"""
Contains calculation functions.
"""
from decimal import getcontext, setcontext, Decimal, DecimalException
from math import inf
from typing import Union, Tuple


def percentage(x: float, y: float) -> Decimal:
    """
    Calculates percentage for part from whole.

    :param x: float value which percentage is calculated.
    :param y: float value from which percentage is taken.
    :return: percentage Decimal value.
    """
    try:
        # getting decimal computations local control context
        decimal_context = getcontext()
        # modifying context to computation needs
        decimal_context.prec = 3
        # setting modified context
        setcontext(decimal_context)
        # creating Decimal instances from float numbers string representations
        # this is needed to avoid problems with creating Decimal instances from floats
        x = Decimal("%.2f" % x)
        y = Decimal("%.2f" % y)
        # calculating and returning percentage value
        return (x / y) * 100
    except DecimalException:
        return Decimal(inf)


def difference(x: float, y: float, num_fmt: str=".2f", include_percentage=True) -> Union[float, Tuple[Decimal, float]]:
    """
    Calculates difference between two float numbers.

    If include_percentage True returns tuple with difference value and its percentage representation.

    :param x: float number which is compared value.
    :param y: float number which is comparable value.
    :param num_fmt: a string that will be used to format a difference value for Decimal instance creation.
    :param include_percentage: if True includes percentage representation in return.
    :return: difference float value or tuple of it plus its percentage representation.
    """
    difference_value = y - x
    if include_percentage:
        return percentage(difference_value, x), Decimal("%{}".format(num_fmt) % difference_value)
    return difference_value
