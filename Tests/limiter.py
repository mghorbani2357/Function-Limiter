import unittest
from unittest import TestCase
from FunctionLimiter.limiter import Limiter
from FunctionLimiter.limiter import RateLimitExceeded
import time
from Tests.exceptions import NotFunctional


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
