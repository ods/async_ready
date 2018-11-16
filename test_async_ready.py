import asyncio
from inspect import isawaitable
import pytest

from async_ready import maybe_await, inline_callbacks


def asyncio_run(coro):
    # Backport of asyncio.run() to Python 3.6
    loop = asyncio.new_event_loop()
    result = loop.run_until_complete(coro)
    loop.close()
    return result


def sync_func(arg):
    return arg

async def async_func(arg):
    return arg

def sync_followup(arg):
    return arg + 23

async def async_followup(arg):
    return arg + 23


async def maybe_await_usage(arg, func):
    maybe_awaitable = func(arg)
    return await maybe_await(maybe_awaitable)

def maybe_await_then_usage(arg, func, followup):
    maybe_awaitable = func(arg)
    return maybe_await(maybe_awaitable).then(followup)

@inline_callbacks
def inline_callbacks_usage(arg, func, followup):
    intermediate = yield func(arg)
    return followup(intermediate)

@inline_callbacks
def inline_callbacks_usage_yield_followup(arg, func, followup):
    intermediate = yield func(arg)
    result = yield followup(intermediate)
    return result

def test_maybe_await_sync():
    awaitable = maybe_await_usage(12, sync_func)
    assert isawaitable(awaitable)
    result = asyncio_run(awaitable)
    assert result == 12

def test_maybe_await_async():
    awaitable = maybe_await_usage(12, async_func)
    assert isawaitable(awaitable)
    result = asyncio_run(awaitable)
    assert result == 12

def test_maybe_await_then_sync():
    result = maybe_await_then_usage(12, sync_func, sync_followup)
    assert result == 35

def test_maybe_await_then_async():
    awaitable = maybe_await_then_usage(12, async_func, sync_followup)
    assert isawaitable(awaitable)
    result = asyncio_run(awaitable)
    assert result == 35

def test_maybe_await_then_sync_followup_is_not_awaited():
    result = maybe_await_then_usage(12, sync_func, async_followup)
    assert isawaitable(result)
    asyncio_run(result)  # To avoid warning

def test_maybe_await_then_async_followup_is_not_awaited():
    awaitable = maybe_await_then_usage(12, async_func, async_followup)
    assert isawaitable(awaitable)
    result = asyncio_run(awaitable)
    assert isawaitable(result)
    asyncio_run(result)  # To avoid warning

def test_inline_callbacks_sync():
    result = inline_callbacks_usage(12, sync_func, sync_followup)
    assert result == 35

def test_inline_callbacks_async():
    awaitable = inline_callbacks_usage(12, async_func, sync_followup)
    assert isawaitable(awaitable)
    result = asyncio_run(awaitable)
    assert result == 35

def test_inline_callbacks_sync_followup_is_not_awaited():
    result = inline_callbacks_usage(12, sync_func, async_followup)
    assert isawaitable(result)
    asyncio_run(result)  # To avoid warning

def test_inline_callbacks_async_followup_is_not_awaited():
    awaitable = inline_callbacks_usage(12, async_func, async_followup)
    assert isawaitable(awaitable)
    result = asyncio_run(awaitable)
    assert isawaitable(result)
    asyncio_run(result)  # To avoid warning

def test_inline_callbacks_sync_yield_followup_is_awaited():
    awaitable = inline_callbacks_usage_yield_followup(
        12, sync_func, async_followup)
    assert isawaitable(awaitable)
    result = asyncio_run(awaitable)
    assert result == 35

def test_inline_callbacks_async_yield_followup_is_awaited():
    awaitable = inline_callbacks_usage_yield_followup(
        12, async_func, async_followup)
    assert isawaitable(awaitable)
    result = asyncio_run(awaitable)
    assert result == 35


if __name__ == '__main__':
    pytest.main()
