.. |license| image:: https://img.shields.io/github/license/mghorbani2357/function-limiter
    :target: https://raw.githubusercontent.com/mghorbani2357/Function-Limiter/master/LICENSE
    :alt: GitHub Licence
    
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
    
.. |readthedocs| image:: https://readthedocs.org/projects/function-limiter/badge/?version=latest
    :target: https://function-limiter.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status


.. |lastcommit| image:: https://img.shields.io/github/last-commit/mghorbani2357/function-limiter 
    :alt: GitHub last commit
    
.. |lastrelease| image:: https://img.shields.io/github/release-date/mghorbani2357/function-limiter   
    :alt: GitHub Release Date

.. |workflow| image:: https://img.shields.io/github/workflow/status/mghorbani2357/function-limiter/main?logo=github   
    :alt: GitHub Workflow Status

*****************
Function-Limiter
*****************

.. class:: center

 |license| |build| |workflow| |codecov| |quality| |coverage| |downloadrate| |downloads| |pypiversion| |format| |wheel| |lastcommit| |lastrelease|


Function-Limiter provides call rate limitation of callable function.

Installation
============

.. code-block:: bash

    pip install Function-Limiter


Quick Start
===========

Add the rate limiter to your function as decorator. The following example uses the default
in memory implementation. ``Limiter()`` create instance of limiter.
By using ``limiter.limit()`` call rate of callable function become limited.
``limiter.limit(limitation, key)`` limitation get the limitation can be assigned number per one of these keywords (second, minute, hour, day, month, year).
Limitation applied on defined key.


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


Custom keying function
======================

You can implement your own function to retrieve the value of rate limit config.

.. code-block:: python

    def limitation():
        return '5/second'

    def key():
        return 'custom key'

    @limiter.limit(limitation, key=key)
    def function():
        print('hello world!')



Redis storage
======================

Redis storage can be involved to lunch multiple instance of application.

.. code-block:: python

    limiter = Limiter(
        storage_uri='redis://ip:port/'
    )

    @limiter.limit('3/minute', 'key')
    def func():
        pass


Exempt key
======================

Exempt key can be used to exempt defined keys. If key and exempt key matched it ignores the limitations

.. code-block:: python

    limiter = Limiter()

    @limiter.limit('3/minute', 'key', exempt='key')
    def func():
        pass

Default values
==============

You can define rate limit default value when the Limiter instance was initialized.
By defining default rate limit values if there isn't any value for the specific key it applies the default value.

.. code-block:: python

    limiter = Limiter(
        default_limitations='3/minute',
        default_key='key',
        default_exempt='key'
    )

    @limiter.limit()
    def func():
        pass
