"""
Actually it ia a clone of https://github.com/seemethere/retry.it with minor changes.
Every original tests are successful, even more.
"""
import functools
import itertools
import time

from decorator import decorator


class _DummyException(Exception):
    pass


def retry(
        exceptions=(Exception,), interval=0, max_retries=10, success=None,
        timeout=-1):
    """Decorator to retry a function 'max_retries' amount of times

    :param tuple exceptions: Exceptions to be caught for retries
    :param int interval: Interval between retries in seconds
    :param int max_retries: Maximum number of retries to have, if
        set to -1 the decorator will loop forever
    :param function success: Function to indicate success criteria
    :param int timeout: Timeout interval in seconds, if -1 will retry forever
    :raises MaximumRetriesExceeded: Maximum number of retries hit without
        reaching the success criteria
    :raises TypeError: Both exceptions and success were left None causing the
        decorator to have no valid exit criteria.

    Example:
        Use it to decorate a function!

        .. sourcecode:: python

            from retry import retry

            @retry(exceptions=(ArithmeticError,), success=lambda x: x > 0)
            def foo(bar):
                if bar < 0:
                    raise ArithmeticError('testing this')
                return bar
            foo(5)
            # Should return 5
            foo(-1)
            # Should raise ArithmeticError
            foo(0)
            # Should raise MaximumRetriesExceeded
    """
    if not exceptions and success is None:
        raise TypeError(
            '`exceptions` and `success` parameter can not both be None')
    # For python 3 compatability
    exceptions = exceptions or (_DummyException,)

    @decorator
    def wrapper(func, *args, **kwargs):
        run_func = functools.partial(func, *args, **kwargs)
        if max_retries < 0:
            iterator = itertools.count()
        else:
            iterator = range(max_retries)
        if timeout >= 0:
            timed_out = time.time() + timeout

        result, exception = None, None
        for num, _ in enumerate(iterator, 1):
            exception = None
            try:
                result = run_func()
                if success is None or success(result):
                    return result
            except exceptions as e:
                if num == max_retries:
                    raise
                else:
                    exception = e
            except Exception as e:
                exception = e
            if timeout >= 0 and time.time() > timed_out:
                break
            else:
                time.sleep(interval)

        if exception:
            raise exception
        else:
            return result
    return wrapper
