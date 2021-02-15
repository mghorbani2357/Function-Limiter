.. |license| image:: https://img.shields.io/pypi/l/Function-Limiter.svg?style=flat
    :target: https://pypi.python.org/pypi/Function-Limiter
    
.. |build| image:: https://travis-ci.com/mghorbani2357/Function-Limiter.svg?branch=master
    :target: https://travis-ci.com/mghorbani2357/Function-Limiter
    
.. |codecov| image:: https://codecov.io/gh/mghorbani2357/Function-Limiter/branch/master/graph/badge.svg?token=V606VBKSGK
    :target: https://codecov.io/gh/mghorbani2357/Function-Limiter

..  |quality| image:: https://api.codacy.com/project/badge/Grade/4ec8eeac03144927aef804e2388b7988
    :target: https://app.codacy.com/gh/mghorbani2357/Function-Limiter?utm_source=github.com&utm_medium=referral&utm_content=mghorbani2357/Function-Limiter&utm_campaign=Badge_Grade
   
.. |coverage| image:: https://app.codacy.com/project/badge/Coverage/ebc9c5345a4f48bda082b09b815cee57   
    :target: https://www.codacy.com/gh/mghorbani2357/Function-Limiter/dashboard?utm_source=github.com&utm_medium=referral&utm_content=mghorbani2357/Function-Limiter&utm_campaign=Badge_Coverage

.. |downloadrate| image:: https://img.shields.io/pypi/dm/Function-Limiter
    :target: https://pypistats.org/packages/function-limiter
    
.. |wheel| image:: https://img.shields.io/pypi/wheel/Function-Limiter  
    :target: https://pypi.python.org/pypi/Function-Limiter
    :alt: PyPI - Wheel
    
.. |pypiversion| image:: https://img.shields.io/pypi/v/Function-Limiter  
    :target: https://pypi.python.org/pypi/Function-Limiter
    :alt: PyPI
    
.. |format| image:: https://img.shields.io/pypi/format/Function-Limiter
    :target: https://pypi.python.org/pypi/Function-Limiter
    :alt: PyPI - Format
    
.. |downloads| image:: https://static.pepy.tech/personalized-badge/function-limiter?period=total&units=international_system&left_color=grey&right_color=blue&left_text=Downloads
    :target: https://pepy.tech/project/function-limiter


*****************
Function-Limiter
*****************

.. class:: center

    |license| |build| |quality| |coverage| |downloadrate| |downloads| |pypiversion| |format| |wheel|


Function-Limiter provides rate limiting features to callable function.

Installation
============

.. code-block:: bash

    pip install Function-Limiter


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
================

The limit string can be a single limit or a delimiter separated string

.. code-block:: python

    @limiter.limit('3/second;10 per minute', 'key')
    def function():
        print('hello world!')

Multiple decorators
===================

The limit string can be a single limit or a delimiter separated string or a combination of both.

.. code-block:: python

    @limiter.limit('3/second', 'key')
    @limiter.limit('10 per minute', 'key')
    def function():
        print('hello world!')


Custom keying function
======================

By default rate limits are applied based on the key function that the Limiter instance was initialized with. You can implement your own function to retrieve the key to rate limit by when decorating individual routes. Take a look at Rate Limit Key Functions for some examples.

.. code-block:: python

    def limitation():
        return '5/second'

    def key():
        return 'custom key'

    @limiter.limit(limitation, key=key)
    def function():
        print('hello world!')

