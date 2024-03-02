import asyncio
import unittest

from core.configs import settings


async def my_func():
    await asyncio.sleep(0.1)
    return True


class BaseTest(unittest.IsolatedAsyncioTestCase):

    async def test_one(self):
        r = await my_func()
        self.assertTrue(r)
