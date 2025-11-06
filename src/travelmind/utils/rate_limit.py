"""
Rate Limiting Utilities

Implements rate limiting for external API calls to respect free tier limits.

Rate limits for different services:
- OpenTripMap: 1 request/second, 500/day
- Open-Meteo: Very generous, ~10k/day
- OSRM: ~2 requests/second (be respectful)
- OpenRouteService: 40 requests/minute (free tier)
- Overpass (OSM): ~2 requests/second

Strategy:
- Token bucket algorithm for short-term rate limiting
- Daily counters for quota management
- Automatic retry with exponential backoff
"""

import asyncio
import time
from collections import defaultdict
from typing import Any, Callable, TypeVar

import httpx


T = TypeVar("T")


class RateLimiter:
    """
    Token bucket rate limiter for API calls.

    Limits requests per second and tracks daily quotas.
    """

    def __init__(
        self,
        requests_per_second: float = 1.0,
        requests_per_day: int | None = None,
    ) -> None:
        """
        Initialize rate limiter.

        Args:
            requests_per_second: Maximum requests per second
            requests_per_day: Optional daily quota
        """
        self.rate = requests_per_second
        self.daily_limit = requests_per_day

        self.tokens = requests_per_second
        self.last_update = time.monotonic()

        self.daily_count = 0
        self.daily_reset_time = time.time() + 86400  # 24 hours

    async def acquire(self) -> None:
        """
        Acquire permission to make a request.

        Blocks until a token is available or raises if daily limit exceeded.
        """
        # Check daily limit
        if self.daily_limit is not None:
            if time.time() >= self.daily_reset_time:
                self.daily_count = 0
                self.daily_reset_time = time.time() + 86400

            if self.daily_count >= self.daily_limit:
                raise RuntimeError(
                    f"Daily rate limit exceeded ({self.daily_limit} requests/day)"
                )

        # Token bucket algorithm
        now = time.monotonic()
        elapsed = now - self.last_update
        self.tokens = min(self.rate, self.tokens + elapsed * self.rate)
        self.last_update = now

        if self.tokens < 1:
            wait_time = (1 - self.tokens) / self.rate
            await asyncio.sleep(wait_time)
            self.tokens = 0
        else:
            self.tokens -= 1

        self.daily_count += 1


# Global rate limiters for each service
_rate_limiters: dict[str, RateLimiter] = {
    "opentripmap": RateLimiter(requests_per_second=1.0, requests_per_day=500),
    "openmeteo": RateLimiter(requests_per_second=5.0),
    "osrm": RateLimiter(requests_per_second=2.0),
    "openrouteservice": RateLimiter(requests_per_second=0.67),  # 40/min
    "overpass": RateLimiter(requests_per_second=2.0),
}


def get_rate_limiter(service: str) -> RateLimiter:
    """
    Get rate limiter for a service.

    Args:
        service: Service name (e.g., "opentripmap")

    Returns:
        RateLimiter instance
    """
    if service not in _rate_limiters:
        # Default: 1 request per second
        _rate_limiters[service] = RateLimiter(requests_per_second=1.0)
    return _rate_limiters[service]


def rate_limited(
    service: str,
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    Decorator to rate-limit async functions.

    Args:
        service: Service name for rate limiting

    Usage:
        @rate_limited("opentripmap")
        async def fetch_poi(poi_id: str) -> dict:
            ...
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        limiter = get_rate_limiter(service)

        async def wrapper(*args: Any, **kwargs: Any) -> T:
            await limiter.acquire()
            return await func(*args, **kwargs)

        return wrapper  # type: ignore

    return decorator


async def retry_with_backoff(
    func: Callable[..., T],
    max_retries: int = 3,
    initial_delay: float = 1.0,
    backoff_factor: float = 2.0,
) -> T:
    """
    Retry an async function with exponential backoff.

    Useful for handling temporary API failures.

    Args:
        func: Async function to retry
        max_retries: Maximum number of retry attempts
        initial_delay: Initial delay in seconds
        backoff_factor: Multiplier for each retry

    Returns:
        Function result

    Raises:
        Last exception if all retries fail
    """
    delay = initial_delay
    last_exception = None

    for attempt in range(max_retries):
        try:
            return await func()
        except (httpx.HTTPError, asyncio.TimeoutError) as e:
            last_exception = e
            if attempt < max_retries - 1:
                await asyncio.sleep(delay)
                delay *= backoff_factor

    raise last_exception  # type: ignore
