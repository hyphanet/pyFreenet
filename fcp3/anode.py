"""An implementation of a freenet client library for
FCP v2, offering considerable flexibility.

This module is prepared for use with the asyncio, async and await
constructs in python3.

Clients should instantiate ANode, then await its methods to perform
tasks with FCP.

It is implemented as a wrapper around the FCPNode and other functions
in node.py.

Example 1:

    import fcp3.anode

    anode = fcp3.anode.ANode()
    try:
        await anode.start()
        await anode.get(...)
        await anode.put(...)
    finally:
        await anode.shutdown()

Example 2: Context manager
    import fcp3.anode

    async with fcp3.anode.ANode() as anode:
        await anode.get(...)
        await anode.put(...)

Example 3: Start put based on created uri before previous upload completed
    import asyncio
    import fcp3.anode

    async with fcp3.anode.ANode() as anode:
        async with asyncio.TaskGroup() as tg:
            uri1 = await anode.put2(tg, ....)
            calculate contents based on uri1
            uri2 = await anode.put2(tg, ...calculated contents...)
            # Both put operations are uploading
            # When both are completed the taskgroup finishes

This was written 2026.
"""

import asyncio
import logging
from functools import wraps
from typing import Any, Self

from .node import FCPNode, \
    FCPGetFailed, FCPPutFailed, FCPProtocolError, FCPException


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
        """Connect to the Hyphanet node.

        TODO: Should not block on the socket operations.
        Fixing this is not a high priority since this method is
        probably only called once anyway.
        """
        self.node = FCPNode(**self.kw)
        self.node.noCloseSocket = False

    async def __aenter__(self) -> Self:
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        await self.shutdown()

    async def shutdown(self) -> None:
        """Connect to the Hyphanet node.

        TODO: Should not block on aquiring lock and perform socket operations.
        """
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
                match result['header']:
                    case 'GetFailed':
                        self._set_exception(FCPGetFailed(result))
                    case 'PutFailed':
                        self._set_exception(FCPPutFailed(result))
                    case 'ProtocolError':
                        self._set_exception(FCPProtocolError(result))
                    case 'IdentifierCollision':
                        self._set_exception(ANode.CallbackException(
                            f'Duplicate job identifier {id}'))
                    case _:
                        self._set_exception(FCPException(result))
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
        When awaited it finishes when the result of the get is available."""
        self.node.get(*args, **kwargs)

    @_asyncify
    def put(self, *args, **kwargs) -> Any:
        """The asynchronous version of node.put().
        When awaited it finishes when inserted."""
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
        to be awaited later.
        """
        assert 'async' not in kwargs
        assert 'callback' not in kwargs

        logging.debug('Starting put2 %s %s', args, kwargs)
        kwargs['async'] = True

        res = get_future()
        keyres = get_future()
        kwargs['callback'] = self.Callback2(res, keyres)

        async def do(args, kwargs):
            self.node.put(*args, **kwargs)
            logging.debug('Queued put2 %s %s %s', args, kwargs, res)
            await kwargs['callback'].get_a_result()

        taskgroup.create_task(do(args, kwargs))
        await keyres
        return keyres.result()
