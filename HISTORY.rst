.. :changelog:

Changelog
=========

v1.2.0
------
Release Date: 2025-02
    * Fractional limitation implemented
    * Redis data storage structure optimized
    * Async. test cases and documentation updated
    * Validator per-process reformatted

v0.2.0
-------
Release Date: 2022-04
    * Redis storage connection updated to use RedisClient.
    * Asynchronous function limitation added.

v0.1.4
-------
Release Date: 2022-04
    * Added support for Redis 4.3.0 and later.
    * Workflow updated.

v0.1.3
-------
Release Date: 2022-04
    * Limitation reset implemented
    * Bug Fixed:
        * Day limitation bug fixed

    * Notice: From next version, limiter must directly import package

v0.1.1
-------
Release Date: 2021-02
    * Bug Fixed:
        * Multiple line decorator doesn't work

v0.1.0
-------
Release Date: 2021-02
    * Set Custom Database name
    * Bug Fixed:
        * Using `per` in limitation doesn't work.
        * Default keys(`limitations`, `key`, `exempt`) doesn't set

v0.0.12
-------
Release Date: 2021-02
    * Exempt key added.

v0.0.11
-------
Release Date: 2021-02
    * Global limitations key added.

v0.0.10
-------
Release Date: 2021-02
    * Global limitations added.

v0.0.9
------
Release Date: 2021-01
    * Rate limit policy changed to successful call.
    * Bug Fixed:
        * Multiple limit doesn't work.

v0.0.8
------
Release Date: 2021-01
    * Bug Fixed:
        * Null key bugs Fixed.

v0.0.7
------
Release Date: 2021-01
    * Bug Fixed.

v0.0.6
------
Release Date: 2021-01
    * Added redis as in memory storage.

v0.0.5
------
Release Date: 2021-01
    * Added garbage collector.

v0.0.4
------
Release Date: 2021-01
    * Added Validator to limiter.

v0.0.3
------
Release Date: 2021-01
    * Added callable function for limitation and key function.

v0.0.2
------
Release Date: 2021-01
    * Bug fixed.

v0.0.1
------
Release Date: 2021-01
    * Basic Function Limiter.