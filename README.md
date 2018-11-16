# async_ready — Primitives to simplify writing code that works in both sync and async environments

Requires Python 3.6 or later. In case you need to support Python 2.7 try using
[promise](https://pypi.org/project/promise/).

## Documentation

### `await maybe_await(maybe_awaitable)`

Converts `maybe_awaitable` to awaitable if it's not already.  This allows you
to accept both ordinary and coroutine functions and with the same code:

```python
async def library_function(maybe_coroutine_func):
    result = await maybe_await(maybe_coroutine_func())
```

### `maybe_await(maybe_awaitable).then(followup_func)`

When `maybe_awaitable` is a coroutine or other awaitable object it is awaited,
then `followup_func` is called with its result. Returns the new coroutine
object for `followup_func`'s result.  When `maybe_awaitable` is not awatiable
(is a result of synchronous function) it's passed to `followup_func` and its
result is returned immediately.

### `@inline_callbacks` decorator

Chains inline callbacks separated with `yield`-s in decorated generator
awaiting each yielded result if needed.  This allows to write code that
works both in synchronous and asynchronous context.  The result is available
synchronously if all callbacks are synchronous, otherwise it returns a
coroutine object.  Example:

```python
@async_ready.inline_callbacks
def library_function(user_maybe_coroutine_func1, user_maybe_coroutine_func2):
    arg1 = some_sync_code()
    result1 = yield user_maybe_coroutine_func1(arg1)
    arg2 = other_sync_code(result1)
    result2 = yield user_maybe_coroutine_func2(arg2)
    return result2
```
