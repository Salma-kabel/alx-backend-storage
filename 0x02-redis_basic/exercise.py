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
    randomkey = method.__qualname__

    @wraps(method)
    def wrapper(self, *args, **kwargs):
        """wrapper method"""
        self._redis.incr(randomKey)
        return method(self, *args, **kwargs)
    return wrapper


def call_history(method: Callable) -> Callable:
    """add input parameters to a list in redis"""
    randomKey = method.__qualname__
    inpt = "".join([randomKey, ":inputs"])
    outpt = "".join([randomKey, ":outputs"])

    @wraps(method)
    def wrapper(self, *args, **kwargs):
        """ Wrapper method """
        self._redis.rpush(i, str(args))
        result = method(self, *args, **kwargs)
        self._redis.rpush(o, str(res))
        return result
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
        randomKey = str(uuid4())
        self._redis.mset({randomKey: data})
        return randomKey

    def get(self, randomKey: str, func: Optional[Callable] = None) \
            -> UnionOfTypes:
        """convert the data back to the desired format"""
        if func:
            return func(self._redis.get(randomKey))
        result = self._redis.get(randomKey)
        return result

    def get_int(self: bytes) -> int:
        """get a number"""
        return int.from_bytes(self, sys.byteorder)

    def get_str(self: bytes) -> str:
        """get a string"""
        return self.decode("utf-8")

    def replay(method: Callable) -> Callable:
        """display the history of calls of a particular function"""
        instance = redis.Redis()
        qname = method.__qualname__
        inpt = instance.lrange(f"{qname}:inputs", 0, -1)
        outpt = instance.lrange(f"{qname}:outputs", 0, -1)
        print("{} was called {} times:".format(qname, len(inpt)))
        for input, output in zip(inpt, outpt):
            print(f"{qname}(*{input.decode('UTF-8')}) -> {output}")
