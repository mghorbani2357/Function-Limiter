import unittest
from unittest import TestCase
from function_limiter.limiter import Limiter
from function_limiter.limiter import RateLimitExceeded
import time
from tests.exceptions import NotFunctional
from multiprocessing import Process


class TestLimiter(TestCase):
    def setUp(self):
        pass

    def test_limiter(self):
        limiter = Limiter()

        @limiter.limit('3/minute', 'key')
        def func():
            pass

        try:
            for i in range(3):
                func()
        except:
            self.assertRaises(ModuleNotFoundError)

        try:
            func()
        except Exception as e:
            self.assertNotEqual(e, RateLimitExceeded)

    def test_callable_function_limiter(self):
        limiter = Limiter()

        def limitations():
            return '3/minute'

        @limiter.limit(limitations, 'key')
        def func():
            pass

        try:
            for i in range(3):
                func()
        except:
            self.assertRaises(ModuleNotFoundError)

        try:
            func()
        except Exception as e:
            self.assertNotEqual(e, RateLimitExceeded)

    def test_multiple_limitations(self):
        limiter = Limiter()

        @limiter.limit('3/minute;1/second', 'key')
        def func():
            pass

        try:
            for i in range(3):
                func()

        except Exception as e:
            self.assertNotEqual(e, RateLimitExceeded)

        try:
            func()
        except Exception as e:
            self.assertRaises(ModuleNotFoundError)

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
