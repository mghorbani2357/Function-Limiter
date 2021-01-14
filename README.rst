.. |license| image:: https://img.shields.io/pypi/l/Function-Limiter.svg?style=flat
    :target: https://pypi.python.org/pypi/Function-Limiter


*************
Function-Limiter
*************
|license|


Function-Limiter provides rate limiting features to callable function.

Quickstart
===========

Add the rate limiter to your function as decorator. The following example uses the default
in memory implementation for storage.


.. code-block:: python

    from FunctionLimiter.limiter import Limiter
    from FunctionLimiter.limiter import RateLimitExceeded
    import time

    limiter = Limiter()


    @limiter.limit('3/second', 'key')
    def function():
        print('hello world!')


    for i in range(5):
        function()
        time.sleep(1)

    for i in range(5):
        function()
        time.sleep(0.9)

