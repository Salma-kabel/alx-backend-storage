#!/usr/bin/env python3
"""Create a Cache class"""


import redis
import sys
from typing import Union, Optional, Callable
from functools import wraps
from uuid import uuid4


UnionOfTypes = Union[str, bytes, int, float]


def count_calls(method: Callable) -> Callable:
    """count how many times methods of the Cache class are called """
    key = method.__qualname__

    @wraps(method)
    def wrapper(self, *args, **kwargs):
        """wrapper method"""
        self._redis.incr(key)
        return method(self, *args, **kwargs)
    return wrapper


def call_history(method: Callable) -> Callable:
    """add input parameters to a list in redis"""
    key = method.__qualname__
    i = "".join([key, ":inputs"])
    o = "".join([key, ":outputs"])

    @wraps(method)
    def wrapper(self, *args, **kwargs):
        """ Wrapper method """
        self._redis.rpush(i, str(args))
        res = method(self, *args, **kwargs)
        self._redis.rpush(o, str(res))
        return res

    return wrapper


class Cache:
    """cache redis class"""

    def __init__(self):
        """constructor of the redis model"""
        self._redis = redis.Redis()
        self._redis.flushdb()

    @count_calls
    @call_history
    def store(self, data: UnionOfTypes) -> str:
        """store the input data in Redis using a
        random key and return the key"""
        key = str(uuid4())
        self._redis.mset({key: data})
        return key

    def get(self, key: str, fn: Optional[Callable] = None) \
            -> UnionOfTypes:
        """convert the data back to the desired format"""
        if fn:
            return fn(self._redis.get(key))
        data = self._redis.get(key)
        return data

    def get_int(self: bytes) -> int:
        """get a number"""
        return int.from_bytes(self, sys.byteorder)

    def get_str(self: bytes) -> str:
        """get a string"""
        return self.decode("utf-8")

    def replay(method: Callable) -> Callable:
        """display the history of calls of a particular function"""
        instance = redis.Redis()
        qn = method.__qualname__
        inputs = instance.lrange(f"{qn}:inputs", 0, -1)
        outputs = instance.lrange(f"{qn}:outputs", 0, -1)
        print("{} was called {} times:".format(qn, len(inputs)))
        for input, output in zip(inputs, outputs):
            print(f"{qn}(*{input.decode('UTF-8')}) -> {output}")
