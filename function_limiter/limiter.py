from functools import wraps
import time
import random
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
    def __init__(self, storage_uri=None):
        """
        Args:
            storage_uri (str): URI of redis.

        """

        #  Todo: Validate storage_uri
        if storage_uri:
            self.storage = redis.from_url(url=storage_uri, db=0)

            if not self.storage.exists('logs'):
                self.logs = self.storage.set('logs', '{}')

            self.logs = json.loads(self.storage.get('logs').decode().replace('\'', '"'))

        else:
            self.storage_uri = None
            self.storage = None
            self.logs = dict()

    @staticmethod
    def __validate_limitations(limitations):
        """
        Returns:
            bool: True if it is valid string, False if it isn't

        """
        if type(limitations) == str or type(limitations) == function:
            if type(limitations) == function:
                _limitations = limitations  # Get backup of limitations function.
                limitations = _limitations()
        else:
            return False

        if limitations[-1] != ';':
            limitations += ';'

        regex_string = r'/^(\d+(\.\d+)?\/(second|minute|hour|week|month|year){1};{1})*$/s'

        regex = re.compile(regex_string)

        if regex.match(limitations):
            return True
        else:
            return False

    def __evaluate_limitations(self, limitations, key):
        """
        Args:
            limitations (str / function): Limitations wanted to apply.
            key (str / function): Key which specifies the limitation.

        Returns:
            bool: True if it permitted, False if otherwise

        """

        # if not self.__validate_limitations(limitations):
        #     return True

        if callable(limitations):
            _limitations = limitations  # Get backup of limitations function.
            limitations = _limitations()

        if callable(key):
            _key = key  # Get Backup of key function.
            key = _key()

        # Todo: Reconsider on bad key actions.

        if key not in self.logs.keys():
            return True

        passed_log = list()
        if self.storage:
            time_logs = json.loads(self.storage.get('logs').decode().replace('\'', '"'))
        else:
            time_logs = self.logs

        limitations.replace(' per ', '/')
        for limitation in limitations.split(';'):
            limit_count, limit_time = limitation.split('/')
            limit_count = float(limit_count)
            period = time_periods[limit_time]
            lap = 1
            garbage_set = set()

            for tick in time_logs[key]:
                if time.time() - tick < period:
                    lap += 1
                else:
                    garbage_set.add(tick)

            if limit_count < lap:
                return False
            passed_log.append(garbage_set)

        else:
            to_delete_time_log = list(set.intersection(*passed_log))
            for item in to_delete_time_log:
                time_logs[key].remove(item)

        if self.storage:
            self.storage.set('logs', str(time_logs))
        else:
            self.logs = time_logs

        return True

    def limit(self, limitations='', key=''):
        """
        Args:
            limitations (str / function): Limitations wanted to apply.
            key (str / function): Key which specifies the limitation.

        Raises:
            RateLimitExceeded (RateLimitExceeded): When callable function reached the limitations.

        Returns:
            limit (function)

        """

        def decorator(function):
            @wraps(function)
            def wrapper(*args, **kwargs):

                if self.__evaluate_limitations(limitations, key):
                    if self.storage:
                        time_logs = json.loads(self.storage.get('logs').decode().replace('\'', '"'))
                    else:
                        time_logs = self.logs

                    if key not in time_logs:
                        time_logs[key] = list()

                    time_logs[key].append(time.time())

                    if self.storage:
                        self.storage.set('logs', str(time_logs))
                    else:
                        self.logs = time_logs
                    return function(*args, **kwargs)
                else:
                    raise RateLimitExceeded

            return wrapper

        return decorator
