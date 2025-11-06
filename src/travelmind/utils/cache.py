"""
Caching Utilities

Provides disk-based caching for API responses using diskcache.

Key features:
- Automatic cache key generation from function args
- TTL (time-to-live) support
- Async function support
- Easy decorator-based usage

Caching strategy:
- POI data: 7 days (static data)
- Weather forecasts: 6 hours (updates throughout day)
- Routes: 30 days (road networks change slowly)
- LLM responses: No cache (varies by query)
"""

import functools
import hashlib
import json
from typing import Any, Callable, TypeVar

from diskcache import Cache

from .config import settings


# Initialize global cache
cache = Cache(str(settings.cache_dir))


T = TypeVar("T")


def cache_key(*args: Any, **kwargs: Any) -> str:
    """
    Generate a cache key from function arguments.

    Args:
        *args: Positional arguments
        **kwargs: Keyword arguments

    Returns:
        MD5 hash of serialized arguments
    """
    key_data = {"args": args, "kwargs": kwargs}
    key_str = json.dumps(key_data, sort_keys=True, default=str)
    return hashlib.md5(key_str.encode()).hexdigest()


def cached(ttl: int | None = None) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    Decorator to cache function results.

    Args:
        ttl: Time-to-live in seconds (None = use default from settings)

    Usage:
        @cached(ttl=3600)
        def expensive_function(x: int) -> int:
            return x * 2
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            key = f"{func.__module__}.{func.__name__}:{cache_key(*args, **kwargs)}"
            result = cache.get(key)

            if result is None:
                result = func(*args, **kwargs)
                expire_time = ttl if ttl is not None else settings.cache_ttl_seconds
                cache.set(key, result, expire=expire_time)

            return result  # type: ignore

        return wrapper

    return decorator


def async_cached(
    ttl: int | None = None,
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    Decorator to cache async function results.

    Args:
        ttl: Time-to-live in seconds (None = use default from settings)

    Usage:
        @async_cached(ttl=3600)
        async def fetch_data(url: str) -> dict:
            async with httpx.AsyncClient() as client:
                response = await client.get(url)
                return response.json()
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> T:
            key = f"{func.__module__}.{func.__name__}:{cache_key(*args, **kwargs)}"
            result = cache.get(key)

            if result is None:
                result = await func(*args, **kwargs)
                expire_time = ttl if ttl is not None else settings.cache_ttl_seconds
                cache.set(key, result, expire=expire_time)

            return result  # type: ignore

        return wrapper  # type: ignore

    return decorator


def clear_cache(pattern: str | None = None) -> int:
    """
    Clear cached entries.

    Args:
        pattern: Optional pattern to match keys (e.g., "weather.*")
                If None, clears entire cache.

    Returns:
        Number of entries cleared
    """
    if pattern is None:
        count = len(cache)
        cache.clear()
        return count
    else:
        # Pattern matching to be implemented
        raise NotImplementedError("Pattern-based cache clearing to be implemented")
