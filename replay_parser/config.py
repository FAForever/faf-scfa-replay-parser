import cProfile
import os
import pstats
from functools import wraps
from io import StringIO
from typing import Callable, Any, Optional

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


def profile_it(sort_by='cumulative'):
    # type: (Optional[str]) -> Callable
    """
    Profiler decorator
    ::
        >>> @profile_it("call")
        >>> def cosi()
        >>>     pass
    """

    def decorator(func):
        # type: (Callable) -> Callable
        @wraps(func)
        def inner(*args, **kwargs):
            # type: (*Any, **Any) -> Any
            profiler = cProfile.Profile()
            profiler.enable()

            ret_val = profiler.runcall(func, *args, **kwargs)

            profiler.disable()
            buff = StringIO()

            stats_printer = pstats.Stats(profiler, stream=buff).sort_stats(sort_by)
            stats_printer.print_stats()

            print(func.__name__)
            print(buff.getvalue())

            return ret_val
        return inner
    return decorator
