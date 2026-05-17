"""
An implementation of a freenet client library for
FCP v2, offering considerable flexibility.

Clients should instantiate ANode, then await its methods to perform
tasks with FCP.

This module is prepared for use with the asyncio, async and await
constructs in python3.

It is a wrapper around the FCPNode and other functions in node.py.

This was written 2026 and released under the GNU Lesser General Public License.
"""

import asyncio
import logging
from functools import wraps
from typing import Any, Self

from .node import FCPNode


def get_future() -> asyncio.Future:
    return asyncio.get_running_loop().create_future()


class ANode:
    """
    Represents an interface to freenet node via its FCP port,
    and exposes primitives for operations in FCP.

    All operations are async operations (awaitable coroutines) to work
    with the python3 asyncio library.
    """

    def __init__(self, **kw) -> None:
        self.kw = kw

    async def start(self) -> None:
        # TODO: Real async operation currently missing
        # The real operation should not block on socket operations.
        # Fixing this is not a high priority since this method is
        # probably only called once anyway.
        self.node = FCPNode(**self.kw)
        self.node.noCloseSocket = False

    async def __aenter__(self) -> Self:
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        await self.shutdown()

    async def shutdown(self) -> None:
        if hasattr(self, 'node'):
            self.node.shutdown()

    class CallbackException(Exception):
        """
        Unexpected message in the interaction to FCPNode.
        """

    class Callback(object):

        def __init__(self, fut: asyncio.Future) -> None:
            self.fut = fut
            self.loop = asyncio.get_running_loop()

        def _set_result(self, result: Any) -> None:
            self.loop.call_soon_threadsafe(self.fut.set_result, result)

        def _set_exception(self, exception: Any) -> None:
            self.loop.call_soon_threadsafe(self.fut.set_exception, exception)

        def __call__(self, status: str, result: Any) -> Any:
            if status == 'successful':
                self._set_result(result)
            elif status == 'pending':
                pass
            elif status == 'failed':
                self._set_exception(result)
            else:
                self._set_exception(ANode.CallbackException(
                    f'Unknown status {status}'))

        def get_result(self) -> Any:
            return self.fut.result()

    def _asyncify(f):
        @wraps(f)
        async def wrap(*args, **kw):
            assert 'async' not in kw
            assert 'callback' not in kw

            logging.debug('Starting %s %s %s', f.__name__, args, kw)
            kw['async'] = True

            res = get_future()
            kw['callback'] = ANode.Callback(res)
            f(*args, **kw)
            await res
            logging.debug('Done %s %s %s %s', f.__name__, args, kw, res)
            return res.result()
        return wrap

    @_asyncify
    def get(self, *args, **kwargs) -> Any:
        """The asynchronous version of node.get().
        When awaited it returns the result of the get."""
        self.node.get(*args, **kwargs)

    @_asyncify
    def put(self, *args, **kwargs) -> Any:
        """The asynchronous version of node.put().
        When awaited it returns the result of the get."""
        self.node.put(*args, **kwargs)

    class Callback2(Callback):
        def __init__(self,
                     res: asyncio.Future,
                     key_fut: asyncio.Future) -> None:
            self.key_fut = key_fut
            super().__init__(res)

        def __set_key_result(self, result: Any) -> None:
            self.loop.call_soon_threadsafe(self.key_fut.set_result, result)

        def __call__(self, status: str, result: Any) -> Any:
            if status == 'pending':
                self.__set_key_result(result['URI'])
            else:
                return ANode.Callback.__call__(self, status, result)

        async def get_a_result(self) -> Any:
            await self.fut
            return self.fut.result()

    async def put2(self, taskgroup: asyncio.TaskGroup, *args, **kwargs) -> str:
        """Put operation that returns the key on await.
        It puts the rest of the operation into the given task group
        to be waited for afterwards.
        """
        assert 'async' not in kwargs
        assert 'callback' not in kwargs

        logging.debug('Starting put2 %s %s', args, kwargs)
        kwargs['async'] = True

        res = get_future()
        keyres = get_future()
        kwargs['callback'] = self.Callback2(res, keyres)
        self.node.put(*args, **kwargs)
        await keyres
        taskgroup.create_task(kwargs['callback'].get_a_result())
        logging.debug('Queued put2 %s %s %s', args, kwargs, res)
        return keyres.result()
