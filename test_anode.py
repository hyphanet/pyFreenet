"""
Testing fcp3.anode against a real node.
"""

import asyncio
import contextlib
import logging
import random
import time
import unittest
import fcp3.anode
from typing import Tuple

from fcp3.node import \
    FCPGetFailed, FCPPutFailed, FCPProtocolError, FCPException


class SmokeTest(unittest.IsolatedAsyncioTestCase):
    uri1 = (
        "USK@E0jWjfYUfJqESuiM~5ZklhTZXKCWapxl~CRj1jmZ-~I," +
        "gl48QSprqZC1mASLbE9EOhQoBa~PheO8r-q9Lqj~uXA,AQACAAE/index.yml/2497"
    )

    async def test_simple_get(self) -> None:
        node = fcp3.anode.ANode()
        try:
            await node.start()
            mimetype, data, details = \
                await node.get(self.uri1, realtime=True, priority=0)
        finally:
            await node.shutdown()
        self.assertEqual(mimetype, 'application/octet-stream')
        self.assertTrue(isinstance(data, bytearray))

    async def test_with_node(self) -> None:
        async with fcp3.anode.ANode() as node:
            mimetype, data, details = \
                await node.get(self.uri1, realtime=True, priority=0)
            self.assertEqual(mimetype, 'application/octet-stream')
            self.assertTrue(isinstance(data, bytearray))


class TestExceptions(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self.anode = fcp3.anode.ANode()  # (verbosity=fcp3.node.DEBUG)

    async def asyncSetUp(self) -> None:
        await self.anode.start()

    async def asyncTearDown(self) -> None:
        await self.anode.shutdown()

    async def testGetFailed(self) -> None:
        with self.assertRaises(FCPGetFailed):
            await self.anode.get(
                "CHK@349wpfKgLk4RPZeHtvfb3mLowuEgwxnndnrKtkOfZ4M,"
                "G1hLoVwaRCVVqRskXb9Bqg8R2aZ2zaEpQP-XXzd4jC4,AAMC--8",
                maxretries=1)

    @unittest.skip("Unclear how to create this error condition")
    async def testPutFailed(self) -> None:
        with self.assertRaises(FCPPutFailed):
            await self.anode.dontknow()

    async def testProtocolError(self) -> None:
        with self.assertRaises(FCPProtocolError):
            await self.anode.get("CHK@somethingthatisnotacorrectkey")

    @unittest.skip("Unclear how to create this error condition")
    async def testCallbackException(self) -> None:
        with self.assertRaises(fcp3.anode.CallbackException):
            await self.anode.dontknow("nonsense")

    @unittest.skip("Unclear how to create this error condition")
    async def testFCPException(self) -> None:
        with self.assertRaises(FCPException):
            await self.anode.dontknow("nonsense")


class MassiveTimes(contextlib.AbstractContextManager):
    def __init__(self, depth: int) -> None:
        self.start_time = time.time()
        self.depth = depth

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        elapsed_time = time.time() - self.start_time
        print(f'Tree with max-depth {self.depth} took {elapsed_time:.1f}s',
              'to create and retrieve.')
        contextlib.AbstractContextManager.__exit__(self,
                                                   exc_type, exc_value,
                                                   traceback)

    def at(self, what: str) -> None:
        until_waiting = time.time() - self.start_time
        print(f'Tree with max-depth {self.depth} took {until_waiting:.1f}s',
              f'until {what}.')


class LimitedTaskGroup(asyncio.TaskGroup):
    def __init__(self, s):
        asyncio.TaskGroup.__init__(self)
        self.sem = asyncio.Semaphore(s)

    async def with_coro(self, coro):
        async with self.sem:
            await coro

    def create_task(self, coro, *, name=None, context=None):
        asyncio.TaskGroup.create_task(self, self.with_coro(coro),
                                      name=name, context=context)


class TestParallel(unittest.IsolatedAsyncioTestCase):
    uri_root = (
        "USK@E0jWjfYUfJqESuiM~5ZklhTZXKCWapxl~CRj1jmZ-~I," +
        "gl48QSprqZC1mASLbE9EOhQoBa~PheO8r-q9Lqj~uXA,AQACAAE/index.yml/"
    )
    DATA = b'some data'
    DATA_KEY = 'CHK@Lw5APCokPPd8SQWxX1V87NwFSIcEGeqYvKnbwgpjIj8'

    def setUp(self) -> None:
        self.anode = fcp3.anode.ANode()  # (verbosity=fcp3.node.DEBUG)

    async def asyncSetUp(self) -> None:
        await self.anode.start()

    async def asyncTearDown(self) -> None:
        await self.anode.shutdown()

    def tearDown(self) -> None:
        self.anode = None

    async def test_one_get(self) -> None:
        mimetype, data, details = \
            await self.anode.get(self.uri_root + "24000",
                                 realtime=True,
                                 priority=0)
        self.assertEqual(mimetype, 'application/octet-stream')
        self.assertTrue(isinstance(data, bytearray))

    async def test_many_gets(self) -> None:
        array = await asyncio.gather(
            *[self.anode.get(self.uri_root + str(i),
                             priority=i % 7)
              for i in range(30)])
        self.assertEqual(len(array), 30)

    async def test_one_put(self) -> None:
        res = await self.anode.put(data=self.DATA)
        self.assertEqual(res[0:10], self.DATA_KEY[0:10])

    async def test_one_put2(self) -> None:
        async with asyncio.TaskGroup() as tg:
            res = await self.anode.put2(tg, data=self.DATA)
            self.assertEqual(res[0:10], self.DATA_KEY[0:10])

    async def test_many_put(self) -> None:
        SIZE = 5
        array = await asyncio.gather(
            *[self.anode.put(data=self.DATA + bytes(str(i), 'utf-8'),
                             priority=i % 7)
              for i in range(SIZE)])
        self.assertEqual(len(array), SIZE)
        for key in array:
            self.assertTrue(isinstance(key, str))
            self.assertEqual(key[0:4], 'CHK@')

    async def create_node_with_leafs(self, size: int) -> Tuple[str, int]:
        if size == 0:
            return ('leaf ' + str(random.randint(0, 10000)), 0)
        await asyncio.sleep(1)
        keys = []
        sum = 0
        for key, count in await asyncio.gather(
                *[self.create_node_with_leafs(
                    random.randint(max(0, size - 3), size - 1))
                  for i in range(size)]):
            keys.append(key)
            sum += count
        return (await self.anode.put(
            data=bytes("size " + str(size) + "\n" +
                       "\n".join(keys), 'utf-8')),
                sum + 1)

    async def check_tree(self, uri: str) -> None:
        mimetype, data, details = \
            await self.anode.get(uri)
        async with asyncio.TaskGroup() as tg:
            for line in str(data, 'utf-8').split('\n'):
                if line.startswith('size '):
                    continue
                if line.startswith('leaf '):
                    continue
                tg.create_task(self.check_tree(line))

    async def run_massive_test_for_build_and_check_trees(self) -> None:
        for s in range(1, 30):
            with MassiveTimes(s):
                key, count = await self.create_node_with_leafs(s)
                print(key, count)
                await self.check_tree(key)

    async def create_node_with_leafs2(self,
                                      size: int,
                                      taskgroup: asyncio.TaskGroup) -> str:
        if size == 0:
            return ('leaf ' + str(random.randint(0, 10000)), 0)
        await asyncio.sleep(1)
        keys = []
        sum = 0
        for key, count in await asyncio.gather(
                *[self.create_node_with_leafs2(
                    random.randint(max(0, size - 3), size - 1), taskgroup)
                  for i in range(size)]):
            keys.append(key)
            sum += count
        return (await self.anode.put2(
            taskgroup,
            data=bytes("size " + str(size) + "\n" +
                       "\n".join(keys), 'utf-8')),
                sum + 1)

    async def run_massive_test_for_build_and_check_trees2(self) -> None:
        """This is not a test of the implementation but a proof of concept.
        It creates a trees of increasing depth and should show that the
        total insert is quicker by letting the put2 return after the key
        then run the inserts in parallel (while the tree is still
        retrieveable).
        Compare with run_massive_test_for_build_and_check_trees."""
        for s in range(1, 30):
            with MassiveTimes(s) as timer:
                async with asyncio.TaskGroup() as tg:
                    key, count = await self.create_node_with_leafs2(s, tg)
                    print(key, count)
                    timer.at('queued')
                timer.at('inserted')
                await self.check_tree(key)

    async def run_massive_test_for_build_and_check_trees3(self) -> None:
        """Same as run_massive_test_for_build_and_check_trees2 but only
        20 outstanding requests at the time."""
        for s in range(1, 30):
            with MassiveTimes(s) as timer:
                async with LimitedTaskGroup(20) as tg:
                    key, count = await self.create_node_with_leafs2(s, tg)
                    print(key, count)
                    timer.at('queued')
                timer.at('inserted')
                await self.check_tree(key)


if __name__ == '__main__':
    log = logging.getLogger('root')
    # log.setLevel(logging.DEBUG)
    unittest.main()
