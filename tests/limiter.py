import asyncio
import time
from contextlib import suppress
from multiprocessing import Process
from unittest import TestCase, IsolatedAsyncioTestCase

import redis

from function_limiter import Limiter
from function_limiter import RateLimitExceeded


class TestSimpleFiveRequest(TestCase):

    def test_five_call(self):
        limiter = Limiter()

        @limiter.limit('5/minute', 'key')
        def func():
            pass

        i = 0
        for i in range(5):
            func()

        self.assertEqual(4, i)

    def test_more_than_limitation_call(self):
        limiter = Limiter()

        @limiter.limit('5/minute', 'key')
        def func():
            pass

        i = 0

        with self.assertRaises(RateLimitExceeded):
            for i in range(6):
                func()

        self.assertEqual(5, i)

    def test_five_call_using_per(self):
        limiter = Limiter()

        @limiter.limit('5 per minute', 'key')
        def func():
            pass

        i = 0

        for i in range(5):
            func()

        self.assertEqual(4, i)


class TestMultipleLimitations(TestCase):

    def test_single_line_limitations(self):
        limiter = Limiter()

        @limiter.limit('1/second;3/minute', 'key')
        def func():
            pass

        i = 0

        for i in range(3):
            func()
            time.sleep(1)

        self.assertEqual(2, i)

    def test_single_line_limitations_more_than_first_limitation(self):
        limiter = Limiter()

        @limiter.limit('1/second;3/minute', 'key')
        def func():
            pass

        i = 0

        with self.assertRaises(RateLimitExceeded):
            for i in range(3):
                func()

        self.assertEqual(1, i)

    def test_single_line_limitations_more_than_second_limitation(self):
        limiter = Limiter()

        @limiter.limit('1/second;3/minute', 'key')
        def func():
            pass

        i = 0

        with self.assertRaises(RateLimitExceeded):
            for i in range(4):
                func()
                time.sleep(1)

        self.assertEqual(3, i)

    # def test_multiple_line_limitations(self):
    #     limiter = Limiter()
    #
    #     @limiter.limit('3/minute', 'key')
    #     @limiter.limit('1/second', 'key')
    #     def func():
    #         pass
    #
    #     i = 0
    #
    #     for i in range(3):
    #         func()
    #         time.sleep(1)
    #
    #     self.assertEqual(i, 2)
    #
    # def test_multiple_line_limitations_more_than_first_limitation(self):
    #     limiter = Limiter()
    #
    #     @limiter.limit('3/minute', 'key')
    #     @limiter.limit('1/second', 'key')
    #     def func():
    #         pass
    #
    #     i = 0
    #     try:
    #         for i in range(3):
    #             func()
    #     except Exception as e:
    #         self.assertIsInstance(e, RateLimitExceeded)
    #         self.assertEqual(i, 2)
    #
    # def test_multiple_line_limitations_more_than_second_limitation(self):
    #     limiter = Limiter()
    #
    #     @limiter.limit('3/minute', 'key')
    #     @limiter.limit('1/second', 'key')
    #     def func():
    #         pass
    #
    #     i = 0
    #     try:
    #         for i in range(4):
    #             func()
    #             time.sleep(1)
    #
    #     except Exception as e:
    #         self.assertIsInstance(e, RateLimitExceeded)
    #         self.assertEqual(i, 2)


class TestCallableFunctionForKeys(TestCase):

    def setUp(self):
        def limitations() -> str:
            return '3/minute'

        self.limitations = limitations

        def key() -> str:
            return 'key'

        self.key = key

        def exempt() -> str:
            return 'key'

        self.exempt = exempt

    def test_callable_function_for_limitations(self):
        limiter = Limiter()

        @limiter.limit(self.limitations, 'key')
        def func():
            pass

        i = 0

        for i in range(3):
            func()

        self.assertEqual(2, i)

    def test_more_than_limitation_call_for_limitations(self):
        limiter = Limiter()

        @limiter.limit(self.limitations, 'key')
        def func():
            pass

        i = 0

        with self.assertRaises(RateLimitExceeded):
            for i in range(4):
                func()

        self.assertEqual(3, i)

    def test_more_than_limitation_call_for_key(self):
        limiter = Limiter()

        @limiter.limit('3/minute', self.key)
        def func():
            pass

        i = 0

        with self.assertRaises(RateLimitExceeded):
            for i in range(4):
                func()

        self.assertEqual(3, i)

    def test_more_than_limitation_call_for_exempt(self):
        limiter = Limiter()

        @limiter.limit('3/minute', 'key', exempt=self.exempt)
        def func():
            pass

        i = 0

        for i in range(4):
            func()

        self.assertEqual(3, i)


class TestDefaultKeys(TestCase):
    def test_default_limitations(self):
        limiter = Limiter(
            default_limitations='3/minute'
        )

        @limiter.limit(None, 'key')
        def func():
            pass

        i = 0
        with self.assertRaises(RateLimitExceeded):
            for i in range(4):
                func()

        self.assertEqual(3, i)

    def test_default_limitations_key(self):
        limiter = Limiter(
            default_key='key'
        )

        @limiter.limit('3/minute')
        def func():
            pass

        i = 0
        with self.assertRaises(RateLimitExceeded):
            for i in range(4):
                func()

        self.assertEqual(3, i)

    def test_default_exempt_key(self):
        limiter = Limiter(
            default_exempt='key'
        )

        @limiter.limit('3/minute', 'key')
        def func():
            pass

        i = 0
        for i in range(10):
            func()

        self.assertEqual(9, i)


class TestExemptKey(TestCase):
    def test_exempt_key(self):
        limiter = Limiter(
            default_key='key'
        )

        @limiter.limit('3/minute', 'key', exempt='key')
        def func():
            pass

        i = 0
        for i in range(10):
            func()

        self.assertEqual(9, i)

    def test_exempt_key_not_equal(self):
        limiter = Limiter(
            default_key='key'
        )

        @limiter.limit('3/minute', 'key', exempt='other-key')
        def func():
            pass

        i = 0
        with self.assertRaises(RateLimitExceeded):
            for i in range(4):
                func()

        self.assertEqual(3, i)


class TestRedis(TestCase):
    def tearDown(self):
        storage = redis.from_url(url='redis://127.0.0.1:6379/', db=0)

        storage.delete('function-limiter')
        storage.delete('custom_database_name')

    def test_redis_for_single_instance(self):
        limiter = Limiter(
            redis_storage=redis.Redis()
        )

        @limiter.limit('3/minute', 'key')
        def func():
            pass

        i = 0

        for i in range(3):
            func()

        self.assertEqual(2, i)

    def test_redis_for_single_instance_over_rate(self):
        limiter = Limiter(
            redis_storage=redis.Redis()
        )

        @limiter.limit('3/minute', 'over-key')
        def func():
            pass

        i = 0

        with self.assertRaises(RateLimitExceeded):
            for i in range(4):
                func()

        self.assertEqual(3, i)

    def test_redis_for_multiple_instance(self):
        limiter = Limiter(
            redis_storage=redis.Redis()
        )

        @limiter.limit('3/minute', 'multiple-instance-key')
        def func():
            pass

        processes = list()
        i = 0

        try:
            for i in range(4):
                processes.append(Process(target=func))

            for process in processes:
                process.start()

            for process in processes:
                process.join()
        except Exception as e:
            self.assertIsInstance(e, RateLimitExceeded)

        self.assertEqual(3, i)

    def test_redis_custom_database_name(self):
        limiter = Limiter(
            database_name='custom_database_name',
            redis_storage=redis.Redis()
        )

        @limiter.limit('3/minute', 'key-k')
        def func():
            pass

        i = 0
        try:
            for i in range(3):
                func()
        except Exception as e:
            self.assertIsInstance(e, RateLimitExceeded)
        self.assertEqual(2, i)


class TestWrongInput(TestCase):
    def test_wrong_limitations_format(self):
        limiter = Limiter()

        @limiter.limit('wrong input', 'key')
        def func():
            pass

        i = 0

        for i in range(10):
            func()

        self.assertEqual(9, i)

    def test_wrong_type_limitations_format(self):
        limiter = Limiter()

        @limiter.limit(0, 'key')
        def func():
            pass

        i = 0

        for i in range(10):
            func()

        self.assertEqual(9, i)


class TestGarbageCollector(TestCase):
    def test_garbage_collector_with_garbage(self):
        limiter = Limiter()

        @limiter.limit('1/second', 'key')
        def func():
            pass

        i = 0

        for i in range(4):
            func()
            time.sleep(1)

        self.assertEqual(3, i)

    def test_garbage_collector_none_garbage(self):
        limiter = Limiter()

        @limiter.limit('3/minute', 'key')
        def func():
            pass

        i = 0

        with self.assertRaises(RateLimitExceeded):
            for i in range(4):
                func()

        self.assertEqual(3, i)


class TestLimitationRest(TestCase):
    def test_reset(self):
        limiter = Limiter()

        @limiter.limit('4/minute', 'key')
        def func():
            pass

        with suppress(RateLimitExceeded):
            for _ in range(5):
                func()

        limiter.reset('key')

        for i in range(4):
            func()

        self.assertEqual(3, i)

    def test_redis_rest(self):
        limiter = Limiter(
            redis_storage=redis.Redis()
        )

        @limiter.limit('3/minute', 'key')
        def func():
            pass

        with suppress(RateLimitExceeded):
            for _ in range(5):
                func()

        limiter.reset('key')

        for i in range(3):
            func()

        self.assertEqual(2, i)

    def tearDown(self):
        with suppress(redis.exceptions.ConnectionError):
            storage = redis.Redis()

            storage.delete('function-limiter')
            storage.delete('custom_database_name')


class TestAsyncLimiter(IsolatedAsyncioTestCase):
    async def test_async_limiter(self):
        limiter = Limiter()

        @limiter.limit('3/minute', 'key')
        async def func():
            await asyncio.sleep(0.5)

        i = 0
        with suppress(RateLimitExceeded):
            for i in range(10):
                await func()

        self.assertEqual(3, i)
