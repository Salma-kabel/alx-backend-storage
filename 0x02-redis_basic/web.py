#!/usr/bin/env python3
"""implement a get_page function"""


import requests
import redis
from typing import Callable
from functools import wraps


redis = redis.Redis()


def wrap_requests(fn: Callable) -> Callable:
    """decorator requests wrapper """

    @wraps(fn)
    def wrapper(url):
        """uses the requests module to obtain the HTML
        content of a particular URL and returns it"""
        redis.incr(f"count:{url}")
        cached_response = redis.get(f"cached:{url}")
        if cached_response:
            return cached_response.decode('utf-8')
        result = fn(url)
        redis.setex(f"cached:{url}", 10, result)
        return result

    return wrapper


@wrap_requests
def get_page(url: str) -> str:
    """track how many times a particular URL was
    accessed in the key "count:{url}"""
    response = requests.get(url)
    return response.text
