"""
Tests for caching utilities
"""

import asyncio

import pytest

from travelmind.utils.cache import async_cached, cache_key, cached, clear_cache


class TestCacheKey:
    """Tests for cache key generation."""

    def test_same_args_same_key(self):
        """Same arguments should produce same key."""
        key1 = cache_key("foo", 123, bar="baz")
        key2 = cache_key("foo", 123, bar="baz")
        assert key1 == key2

    def test_different_args_different_key(self):
        """Different arguments should produce different keys."""
        key1 = cache_key("foo", 123)
        key2 = cache_key("foo", 456)
        assert key1 != key2

    def test_kwargs_order_independent(self):
        """Kwargs in different order should produce same key."""
        key1 = cache_key(a=1, b=2, c=3)
        key2 = cache_key(c=3, a=1, b=2)
        assert key1 == key2


class TestCached:
    """Tests for @cached decorator."""

    def test_function_result_cached(self):
        """Function result should be cached on first call."""
        call_count = 0

        @cached(ttl=60)
        def expensive_function(x: int) -> int:
            nonlocal call_count
            call_count += 1
            return x * 2

        result1 = expensive_function(5)
        result2 = expensive_function(5)

        assert result1 == 10
        assert result2 == 10
        assert call_count == 1  # Only called once, second was cached

    def test_different_args_not_cached(self):
        """Different arguments should not use cached result."""
        call_count = 0

        @cached(ttl=60)
        def expensive_function(x: int) -> int:
            nonlocal call_count
            call_count += 1
            return x * 2

        result1 = expensive_function(5)
        result2 = expensive_function(10)

        assert result1 == 10
        assert result2 == 20
        assert call_count == 2  # Called twice with different args


class TestAsyncCached:
    """Tests for @async_cached decorator."""

    @pytest.mark.asyncio
    async def test_async_function_cached(self):
        """Async function result should be cached."""
        call_count = 0

        @async_cached(ttl=60)
        async def async_expensive(x: int) -> int:
            nonlocal call_count
            call_count += 1
            await asyncio.sleep(0.01)
            return x * 2

        result1 = await async_expensive(5)
        result2 = await async_expensive(5)

        assert result1 == 10
        assert result2 == 10
        assert call_count == 1


class TestClearCache:
    """Tests for cache clearing."""

    def test_clear_all(self):
        """Should clear entire cache."""
        @cached(ttl=60)
        def func(x: int) -> int:
            return x * 2

        func(1)
        func(2)
        func(3)

        count = clear_cache()
        assert count >= 3  # At least our 3 entries
