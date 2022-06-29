"""Function-Limiter Extension for limiting callable functions."""
import asyncio
import json
import re
import time
from contextlib import suppress
from functools import wraps

import redis


class RateLimitExceeded(Exception):
    pass


time_periods = {
    'second': 1,
    'minute': 60,
    'hour': 60 * 60,
    'day': 60 * 60 * 24,
    'week': 60 * 60 * 24 * 7,
    'month': 60 * 60 * 24 * 30,
    'year': 60 * 60 * 24 * 365,
}


class Limiter(object):
    __database_name = 'function-limiter'
    __limiter_keys = list()

    def __init__(self, redis_storage=None, default_limitations=None, default_key=None, default_exempt=None,
                 database_name=None):
        """
        Args:
            redis_storage (redis.Redis): Redis storage.
            default_limitations (str|function|None): Global limitations
            default_key (str|function|None): Global limitations key
            default_exempt (str|function|None): Exempt key used to decide if the rate limit should skipped.

        """
        if database_name is not None:
            self.__database_name = database_name

        if redis_storage:
            self.redis_storage = redis_storage

            if not self.redis_storage.exists(self.__database_name):
                self.logs = self.redis_storage.set(self.__database_name, '{}')

            self.logs = json.loads(self.redis_storage.get(self.__database_name).decode())

        else:
            self.redis_storage = None
            self.logs = dict()

        self.default_limitations = default_limitations
        self.default_key = default_key
        self.default_exempt = default_exempt

    @staticmethod
    def __validate_limitations(limitations):
        """
        Returns:
            bool: True if it is valid string, False if it isn't

        """
        if not isinstance(limitations, str):
            return False

        if limitations[-1] != ';':  # If limitations doesn't end with `;`
            limitations += ';'  # Add `;` to end of the string

        # Check limitation must fallow `count per period;`
        regex_string = r'((?:\d+(?:.\d+)?)(?:\/| per )(?:second|minute|hour|day|week|month|year)(?:;|,))'

        regex = re.compile(regex_string)

        if regex.match(limitations):  # If matches return true to continue the rule
            return True
        else:  # otherwise return False to allow to execute the function
            return False

    def __garbage_collector(self, limitations, key):
        """
        Args:
            limitations (str|function): Limitations wanted to apply.
            key (str|function): Key which specifies the limitation.

        """
        passed_log = list()

        for limitation in limitations.split(';'):
            # limit_count, limit_time = limitation.split('/')
            limit_time = limitation.split('/')[1]
            period = time_periods[limit_time]
            garbage_set = set()

            for tick in self.logs[key]:
                if time.time() - tick >= period:
                    garbage_set.add(tick)

            passed_log.append(garbage_set)

        for item in list(set.intersection(*passed_log)):
            self.logs[key].remove(item)

    def __evaluate_limitations(self, limitations, key):
        """
        Args:
            limitations (str|function): Limitations wanted to apply.
            key (str|function): Key which specifies the limitation.

        Returns:
            bool: True if it permitted, False if otherwise

        """
        if not self.__validate_limitations(limitations):
            return True

        limitations = limitations.replace('per', '/')
        limitations = limitations.replace(' ', '')
        limitations = limitations.replace(',', ';')

        self.__garbage_collector(limitations, key)

        for limitation in limitations.split(';'):
            limit_count, limit_time = limitation.split('/')
            limit_count = float(limit_count)
            period = time_periods[limit_time]
            lap = 0

            for tick in self.logs[key]:
                if time.time() - tick < period:
                    lap += 1

            if limit_count <= lap:
                return False

        return True

    def limit(self, limitations=None, key=None, exempt=None):
        """
        Args:
            limitations (str|function|NoneType): Limitations wanted to apply.
            key (str|function|NoneType): Key which specifies the limitation.
            exempt (str|function|NoneType): Exempt key used to decide if the rate limit should skipped.

        Raises:
            RateLimitExceeded (RateLimitExceeded): When callable function reached the limitations.

        Returns:
            function: Limited function.

        """

        def decorator(function):
            if asyncio.iscoroutinefunction(function):
                @wraps(function)
                async def wrapper(*args, **kwargs):
                    self.__limitation_check(limitations, key, exempt)
                    return await function(*args, **kwargs)
            else:
                @wraps(function)
                def wrapper(*args, **kwargs):
                    self.__limitation_check(limitations, key, exempt)
                    return function(*args, **kwargs)

            return wrapper

        return decorator

    def __limitation_check(self, limitations, key, exempt):
        if self.redis_storage:
            self.logs = json.loads(self.redis_storage.get(self.__database_name).decode())

        _key = key() if callable(key) else key
        _limitations = limitations() if callable(limitations) else limitations
        _exempt = exempt() if callable(exempt) else exempt

        if _limitations is None and self.default_limitations:
            _limitations = self.default_limitations

        if _key is None and self.default_key:
            _key = self.default_key

        if exempt is None and self.default_exempt:
            _exempt = self.default_exempt

        if not (_key is None or _key == _exempt):
            # self.__limiter_keys.append(_key)
            # if self.__limiter_keys.count(_key) <= 1:

            if _key not in self.logs:
                self.logs[_key] = list()

            if not self.__evaluate_limitations(_limitations, _key):
                raise RateLimitExceeded

            self.logs[_key].append(time.time())

            if self.redis_storage:
                self.redis_storage.set(self.__database_name, json.dumps(self.logs))

            # if self.__limiter_keys.__len__() > 0:
            #     self.__limiter_keys.pop(0)

    def reset(self, key):
        """
            Args:
                key (str|function|NoneType): Key which specifies the limitation.
        """

        _key = key() if callable(key) else key

        if self.redis_storage:
            self.logs = json.loads(self.redis_storage.get(self.__database_name).decode())

        with suppress(KeyError):
            del self.logs[_key]

        if self.redis_storage:
            self.redis_storage.set(self.__database_name, json.dumps(self.logs))
