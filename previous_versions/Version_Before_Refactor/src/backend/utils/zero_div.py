def zero_div(x, y):
    try:
        return x / y
    except ZeroDivisionError:
        return 0
