import functools
import inspect


class maybe_await:
    """
    Wrapper for result of function or coroutine to pass to next function or
    coroutine. Useful to write code that can be used in both sync and async
    environment.

    Usage:
        maybe_awaitable = func_or_coroutine()
        result = maybe_await(maybe_awaitable).then(followup_func)

    The result is available synchronously if func_or_coroutine is synchronous,
    and coroutine object if maybe_awaitable is coroutine.
    """

    def __init__(self, maybe_awaitable):
        self.maybe_awaitable = maybe_awaitable

    def __await__(self):
        if inspect.isawaitable(self.maybe_awaitable):
            result = yield from self.maybe_awaitable.__await__()
        else:
            result = self.maybe_awaitable
        return result

    def then(self, func):
        if inspect.isawaitable(self.maybe_awaitable):
            return self._async_then(func)
        else:
            return func(self.maybe_awaitable)

    async def _async_then(self, func):
        return func(await self.maybe_awaitable)


class _CallbacksIter:

    def __init__(self, it):
        self.it = it

    def loop(self):
        value = None
        try:
            while True:
                value = self.it.send(value)
                if inspect.isawaitable(value):
                    return self._async_loop(value)
        except StopIteration as exc:
            return exc.value

    async def _async_loop(self, value):
        value = await value
        try:
            while True:
                value = self.it.send(value)
                if inspect.isawaitable(value):
                    value = await value
        except StopIteration as exc:
            return exc.value


def inline_callbacks(generator):
    """
    Chains inline callbacks separated with `yield`-s in decorated generator
    awaiting each yielded result if needed.  This allows to write code that
    works both in synchronous and asynchronous context.  The result is
    available synchronously if all callbacks are synchronous, otherwise it
    returns coroutine object.

    Example:

        @inline_callbacks
        def method(a):
            b = yield maybe_async_func(a)
            c = certainly_sync_func(b)
            d = yield other_maybe_async_func(c)
            return d
    """

    @functools.wraps(generator)
    def wrapper(*args, **kwargs):
        it = _CallbacksIter(generator(*args, **kwargs))
        return it.loop()

    return wrapper
