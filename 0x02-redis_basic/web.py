import requests
from typing import Callable
from functools import wraps


redis = redis.Redis()


import time


def cache_result(duration=10):
    def decorator(func):
        cache = {}

        def wrapper(url):
            if url in cache and time.time() - cache[url]['timestamp'] < duration:
                return cache[url]['content']
            else:
                content = func(url)
                cache[url] = {'content': content, 'timestamp': time.time()}
                return content

        return wrapper

    return decorator

@cache_result()
def get_page(url: str) -> str:
    response = requests.get(url)
    return response.text

