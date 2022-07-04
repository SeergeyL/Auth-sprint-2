import time
from functools import wraps
from types import FunctionType, GeneratorType
from typing import Any

import psycopg2
import redis

CONNECTION_ERRORS = (
    psycopg2.OperationalError,
    redis.RedisError
)


def backoff(
    start_sleep_time: int = 0.1,
    factor: int = 2,
    border_sleep_time: int = 10
) -> FunctionType:
    """
    Функция для повторного выполнения функции через некоторое время, если возникла ошибка.
    Использует наивный экспоненциальный рост времени повтора (factor)
    до граничного времени ожидания (border_sleep_time)
    Формула:
        t = start_sleep_time * 2^(n) if t < border_sleep_time
        t = border_sleep_time if t >= border_sleep_time
    :param start_sleep_time: начальное время повтора
    :param factor: во сколько раз нужно увеличить время ожидания
    :param border_sleep_time: граничное время ожидания
    :return: результат выполнения функции
    """
    def func_wrapper(func: FunctionType) -> FunctionType:
        @wraps(func)
        def inner(*args: Any, **kwargs: Any) -> Any:
            n = 0
            t = start_sleep_time
            while True:
                try:
                    result = func(*args, **kwargs)
                    if isinstance(result, GeneratorType):
                        result = list(result)
                except CONNECTION_ERRORS:
                    t = start_sleep_time * factor ** n
                    if t >= border_sleep_time:
                        t = border_sleep_time
                    else:
                        n += 1
                    time.sleep(t)
                else:
                    return result
        return inner
    return func_wrapper
