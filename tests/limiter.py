from unittest import TestCase
from function_limiter.limiter import Limiter
from function_limiter.limiter import RateLimitExceeded
import time
from multiprocessing import Process


class TestSimpleFiveRequest(TestCase):

    def test_five_call(self):
        limiter = Limiter()

        @limiter.limit('5/minute', 'key')
        def func():
            pass

        i = 0

        try:
            for i in range(5):
                func()
        except Exception as e:
            self.assertEqual(e, RateLimitExceeded)
            self.assertEqual(i, 4)

    def test_more_than_limitation_call(self):
        limiter = Limiter()

        @limiter.limit('5/minute', 'key')
        def func():
            pass

        i = 0

        try:
            for i in range(6):
                func()
        except Exception as e:
            self.assertNotEqual(e, RateLimitExceeded)
            self.assertEqual(i, 5)

    def test_five_call_using_per(self):
        limiter = Limiter()

        @limiter.limit('5 per minute', 'key')
        def func():
            pass

        i = 0

        try:
            for i in range(5):
                func()
        except Exception as e:
            self.assertNotEqual(e, RateLimitExceeded)
            self.assertEqual(i, 4)


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

        self.assertEqual(i, 2)

    def test_single_line_limitations_more_than_first_limitation(self):
        limiter = Limiter()

        @limiter.limit('1/second;3/minute', 'key')
        def func():
            pass

        i = 0

        try:
            for i in range(3):
                func()
        except Exception as e:
            self.assertNotEqual(e, RateLimitExceeded)
            self.assertEqual(i, 1)

    def test_single_line_limitations_more_than_second_limitation(self):
        limiter = Limiter()

        @limiter.limit('1/second;3/minute', 'key')
        def func():
            pass

        i = 0

        try:
            for i in range(4):
                func()
                time.sleep(1)

        except Exception as e:
            self.assertNotEqual(e, RateLimitExceeded)
            self.assertEqual(i, 3)

    def test_multiple_line_limitations(self):
        limiter = Limiter()

        @limiter.limit('3/minute', 'key')
        @limiter.limit('1/second', 'key')
        def func():
            pass

        i = 0

        for i in range(3):
            func()
            time.sleep(1)

        self.assertEqual(i, 2)

    def test_multiple_line_limitations_more_than_first_limitation(self):
        limiter = Limiter()

        @limiter.limit('3/minute', 'key')
        @limiter.limit('1/second', 'key')
        def func():
            pass

        i = 0
        try:
            for i in range(3):
                func()
        except Exception as e:
            self.assertNotEqual(e, RateLimitExceeded)
            self.assertEqual(i, 2)

    def test_multiple_line_limitations_more_than_second_limitation(self):
        limiter = Limiter()

        @limiter.limit('3/minute', 'key')
        @limiter.limit('1/second', 'key')
        def func():
            pass

        i = 0
        try:
            for i in range(4):
                func()
                time.sleep(1)

        except Exception as e:
            self.assertNotEqual(e, RateLimitExceeded)
            self.assertEqual(i, 2)


class TestLimiter(TestCase):

    def test_callable_function_limiter(self):
        limiter = Limiter()

        def limitations() -> str:
            return '3/minute'

        @limiter.limit(limitations, 'key')
        def func():
            pass

        for i in range(3):
            func()

        try:
            func()
        except Exception as e:
            self.assertNotEqual(e, RateLimitExceeded)

    def test_multiple_limitations(self):
        limiter = Limiter()

        @limiter.limit('1/second;3/minute', 'key')
        def func():
            pass

        for i in range(3):
            func()
            time.sleep(1)

        try:
            func()
        except Exception as e:
            self.assertNotEqual(e, RateLimitExceeded)

    def test_global_limitations(self):
        limiter = Limiter(
            default_limitations='3/minute'
        )

        @limiter.limit(None, 'key')
        def func():
            pass

        for i in range(3):
            func()

        try:
            func()
        except Exception as e:
            self.assertNotEqual(e, RateLimitExceeded)

    def test_global_limitations_key(self):
        limiter = Limiter(
            default_key='key'
        )

        @limiter.limit('3/minute')
        def func():
            pass

        for i in range(3):
            func()

        try:
            func()
        except Exception as e:
            self.assertNotEqual(e, RateLimitExceeded)

    def test_exempt_key(self):
        limiter = Limiter(
            default_key='key'
        )

        @limiter.limit('3/minute', 'key', exempt='key')
        def func():
            pass

        for i in range(10):
            func()

        try:
            func()
        except Exception as e:
            self.assertEqual(e, RateLimitExceeded)


class TestRedis(TestCase):

    def test_redis_for_single_instance(self):
        storage_uri = 'redis://127.0.0.1:6379/'
        limiter = Limiter(storage_uri=storage_uri)

        @limiter.limit('3/minute', 'key')
        def func():
            print('hello world!')

        try:
            for i in range(3):
                func()
        except:
            self.assertRaises(ModuleNotFoundError)

        try:
            func()
        except Exception as e:
            self.assertNotEqual(e, RateLimitExceeded)

    def test_redis_for_multiple_instance(self):
        storage_uri = 'redis://127.0.0.1:6379/'
        limiter = Limiter(storage_uri=storage_uri)

        @limiter.limit('3/minute', 'key')
        def func():
            pass

        try:
            processes = list()
            for i in range(3):
                processes.append(Process(target=func))

            for process in processes:
                process.start()

            for process in processes:
                process.join()
        except:
            self.assertRaises(ModuleNotFoundError)

        try:
            process = Process(target=func)
            process.start()
            process.join()
        except Exception as e:
            self.assertNotEqual(e, RateLimitExceeded)
