import cProfile
import os
import pstats
from functools import wraps
from io import StringIO
from typing import Callable, Any, Optional

DEBUG = bool(os.getenv("SCFA_PARSER_DEBUG", False))


def debug(func: Callable) -> Callable:
    """
    Used for functions debug call
    """
    if not DEBUG:
        return func

    @wraps(func)
    def wrapper(self, *args: Any, **kwargs: Any) -> Any:
        result = func(self, *args, **kwargs)
        if DEBUG:
            print("{}(*args={}, **kwargs={})".format(func.__name__, args, kwargs), "->", result)
        return result
    return wrapper


def profile_it(sort_by: Optional[str] = 'cumulative') -> Callable:
    """
    Profiler decorator
    ::
        >>> @profile_it("call")
        >>> def func():
        >>>     pass
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def inner(*args: Any, **kwargs: Any) -> Any:
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
