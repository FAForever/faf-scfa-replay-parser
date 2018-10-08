import os
from functools import wraps

DEBUG = bool(os.getenv("SCFA_PARSER_DEBUG", False))


def debug(func):
    """
    Used for functions debug call
    """
    if not DEBUG:
        return func

    @wraps(func)
    def wrapper(self, *args, **kwargs):
        result = func(self, *args, **kwargs)
        if DEBUG:
            print("{}(*args={}, **kwargs={})".format(func.__name__, args, kwargs), "->", result)
        return result
    return wrapper
