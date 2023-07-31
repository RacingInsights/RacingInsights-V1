def zero_div(x, y):
    """Returns zero in case of division by zero"""
    try:
        return x / y
    except ZeroDivisionError:
        return 0
