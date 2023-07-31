import logging
from typing import Callable


def exception_handler(func: Callable):
    """
    Is used as a decorator to catch any exceptions arising related to the telemetry.

    Inspired by:
        https://medium.com/swlh/handling-exceptions-in-python-a-cleaner-way-using-decorators-fae22aa0abec

    :param func:
    :return:
    """
    def inner_function(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except Exception as e:
            logging.exception(e)

    return inner_function
