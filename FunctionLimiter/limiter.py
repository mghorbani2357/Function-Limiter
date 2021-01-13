from functools import wraps
import time
import random


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

    def __evaluate_limitations(self, limitations, key):
        """
        Args:
            limitations (str): Limitations wanted to apply.
            key (str): Key which specifies the limitation.

        Returns:
            __evaluate_limitations (bool)
            True if it permitted, False if otherwise

        """

        # Todo: Reconsider on bad key actions.

        if key not in self.timer.keys():
            return True

        # Todo: Validate limitation data.

        limitations.replace(' per ', '/')
        for limitation in limitations.split(';'):
            limit_count, limit_time = limitation.split('/')
            limit_count = float(limit_count)
            period = time_periods[limit_time]
            lap = 1

            for tick in self.timer[key]:
                if time.time() - tick < period:
                    lap += 1
                    # time_log[key].remove(tick)

            if limit_count < lap:
                return False

        return True

    def limit(self, limitations='', key=''):
        """
        Args:
            limitations (str): Limitations wanted to apply.
            key (str): Key which specifies the limitation.

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
