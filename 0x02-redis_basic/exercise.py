#!/usr/bin/env python3
"""Create a Cache class"""


import redis
import sys
from typing import Union, Optional, Callable
from functools import wraps
from uuid import uuid4


UnionOfTypes = Union[str, bytes, int, float]


def count_calls(method: Callable) -> Callable:
    """Count how many times methods of the Cache class are called"""
    randomKey = method.__qualname__

    @wraps(method)
    def wrapper(self, *args, **kwargs):
        """Wrapper method"""
        self._redis.incr(randomKey)
        return method(self, *args, **kwargs)

    return wrapper

def call_history(method: Callable) -> Callable:
    """Add input parameters to a list in Redis"""
    randomKey = method.__qualname__
    inpt = "".join([randomKey, ":inputs"])
    outpt = "".join([randomKey, ":outputs"])

    @wraps(method)
    def wrapper(self, *args, **kwargs):
        """Wrapper method"""
        self._redis.rpush(inpt, str(args))
        res = method(self, *args, **kwargs)
        self._redis.rpush(outpt, str(res))
        return res

    return wrapper

class Cache:
    """Cache Redis class"""

    def __init__(self):
        """Constructor of the Redis model"""
        self._redis = redis.Redis()
        self._redis.flushdb()

    @count_calls
    @call_history
    def store(self, data: UnionOfTypes) -> str:
        """Store the input data in Redis using a
        random key and return the key"""
        randomKey = str(uuid4())
        self._redis.mset({randomKey: data})
        return randomKey

    def get(self, randomKey: str, func: Optional[Callable] = None) -> UnionOfTypes:
        """Convert the data back to the desired format"""
        if func:
            return func(self._redis.get(randomKey))
        res = self._redis.get(randomKey)
        return res

    def get_int(self: bytes) -> int:
        """Get a number"""
        return int.from_bytes(self, sys.byteorder)

    def get_str(self: bytes) -> str:
        """Get a string"""
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
