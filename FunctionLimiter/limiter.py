from functools import wraps
import time
import random
import re


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
    def __init__(self):
        self.timer = dict()

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

        if not self.__validate_limitations(limitations):
            return True

        if callable(limitations):
            _limitations = limitations  # Get backup of limitations function.
            limitations = _limitations()

        if callable(key):
            _key = key  # Get Backup of key function.
            key = _key()

        # Todo: Reconsider on bad key actions.

        if key not in self.timer.keys():
            return True

        passed_log = list()

        limitations.replace(' per ', '/')
        for limitation in limitations.split(';'):
            limit_count, limit_time = limitation.split('/')
            limit_count = float(limit_count)
            period = time_periods[limit_time]
            lap = 1
            garbage_set = set()

            for tick in self.timer[key]:
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
                self.timer.pop(item)

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
                if key not in self.timer.keys():
                    self.timer[key] = list()

                if self.__evaluate_limitations(limitations, key):
                    self.timer[key].append(time.time())
                    return function(*args, **kwargs)
                else:
                    raise RateLimitExceeded

            return wrapper

        return decorator
