from functools import wraps
import time
import re
import redis
import json


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
    __database_name = 'logs'

    def __init__(self, storage_uri=None, default_limitations=None, default_key=None, default_exempt=None):
        """
        Args:
            storage_uri (str): URI of redis.
            default_limitations (str|function|None): Global limitations
            default_key (str|function|None): Global limitations key
            default_exempt (str|function|None): Exempt key used to decide if the rate limit should skipped.

        Todo:
            * Add exempt testcases
        """

        if storage_uri:
            self.storage = redis.from_url(url=storage_uri, db=0)

            if not self.storage.exists(self.__database_name):
                self.logs = self.storage.set(self.__database_name, '{}')

            self.logs = json.loads(self.storage.get(self.__database_name).decode().replace('\'', '"'))

        else:
            self.storage_uri = None
            self.storage = None
            self.default_limitations = default_limitations
            self.default_key = default_key
            self.default_exempt = default_exempt
            self.logs = dict()

    @staticmethod
    def __validate_limitations(limitations):
        """
        Returns:
            bool: True if it is valid string, False if it isn't

        """
        if isinstance(limitations, str):
            return False

        if limitations[-1] != ';':
            limitations += ';'

        regex_string = r'((?:\d+(?:.\d+)?)(?:\/| per )(?:second|minute|hour|week|month|year)(?:;|,))'

        regex = re.compile(regex_string)

        if regex.match(limitations):
            return True
        else:
            return False

    def __garbage_collector(self, limitations, key):
        """
        Args:
            limitations (str|function): Limitations wanted to apply.
            key (str|function): Key which specifies the limitation.

        """

        passed_log = list()

        for limitation in limitations.split(';'):
            limit_count, limit_time = limitation.split('/')
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

        self.__garbage_collector(limitations, key)

        limitations.replace(' per ', '/')
        limitations.replace(' ', '')
        limitations.replace(',', ';')

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
            exempt (str|function|None): Exempt key used to decide if the rate limit should skipped.

        Raises:
            RateLimitExceeded (RateLimitExceeded): When callable function reached the limitations.

        Returns:
            function: Limited function.

        """

        def decorator(function):
            @wraps(function)
            def wrapper(*args, **kwargs):
                if self.storage:
                    self.logs = json.loads(self.storage.get(self.__database_name).decode().replace('\'', '"'))

                _key = key() if callable(key) else key
                _limitations = limitations() if callable(limitations) else limitations
                _exempt = exempt() if callable(exempt) else exempt

                if not _limitations and self.default_limitations:
                    _limitations = self.default_limitations

                if not _key and self.default_key:
                    _key = self.default_key

                if not exempt and self.default_exempt:
                    _exempt = self.default_exempt

                if not (_key is None or _key == _exempt):

                    if _key not in self.logs:
                        self.logs[_key] = list()

                    if not self.__evaluate_limitations(_limitations, _key):
                        raise RateLimitExceeded

                    self.logs[_key].append(time.time())

                    if self.storage:
                        self.storage.set(self.__database_name, str(self.logs))

                return function(*args, **kwargs)

            return wrapper

        return decorator
