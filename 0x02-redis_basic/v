#!/usr/bin/env python3
"""implement a get_page function"""


import requests
import redis
from typing import Callable
from functools import wraps


redis = redis.Redis()


def wrap_requests(func: Callable) -> Callable:
    """decorator requests wrapper """

    @wraps(fn)
    def wrapper(url):
        """uses the requests module to obtain the HTML
        content of a particular URL and returns it"""
        redis.incr(f"count:{url}")
        res = redis.get(f"cached:{url}")
        if res:
            return res.decode('utf-8')
        result = func(url)
        redis.setex(f"cached:{url}", 10, result)
        return result

    return wrapper


@wrap_requests
def get_page(url: str) -> str:
    """track how many times a particular URL was
    accessed in the key "count:{url}"""
    res = requests.get(url)
    return res.text
