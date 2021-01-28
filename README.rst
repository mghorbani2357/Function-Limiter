.. |license| image:: https://img.shields.io/pypi/l/Function-Limiter.svg?style=flat
    :target: https://pypi.python.org/pypi/Function-Limiter


*****************
Function-Limiter
*****************
|license|


Function-Limiter provides rate limiting features to callable function.

Installation
============

.. code-block:: bash

    pip install Flask-Limiter


Quick Start
===========

Add the rate limiter to your function as decorator. The following example uses the default
in memory implementation for storage.

The decorators made available as instance methods of the Limiter instance are ``Limiter``.

.. code-block:: python

    from function_limiter.limiter import Limiter
    from function_limiter.limiter import RateLimitExceeded
    import time

    limiter = Limiter()


    @limiter.limit('3/second', 'key')
    def function():
        print('hello world!')


.. code-block:: python

    from function_limiter.limiter import Limiter
    from function_limiter.limiter import RateLimitExceeded
    import time

    storage_uri = 'redis://ip:port/'
    limiter = Limiter(
            storage_uri=storage_uri
        )


There are a few ways of using this decorator depending on your preference and use-case.


Single decorator
****************

The limit string can be a single limit or a delimiter separated string

.. code-block:: python

    @limiter.limit('3/second;10 per minute', 'key')
    def function():
        print('hello world!')

Multiple decorators
*******************

The limit string can be a single limit or a delimiter separated string or a combination of both.

.. code-block:: python

    @limiter.limit('3/second', 'key')
    @limiter.limit('10 per minute', 'key')
    def function():
        print('hello world!')


Custom keying function
**********************

By default rate limits are applied based on the key function that the Limiter instance was initialized with. You can implement your own function to retrieve the key to rate limit by when decorating individual routes. Take a look at Rate Limit Key Functions for some examples.

.. code-block:: python

    def limitation():
        return '5/second'

    def key():
        return 'custom key'

    @limiter.limit(limitation, key=key)
    def function():
        print('hello world!')

