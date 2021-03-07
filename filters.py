from aiogram import types
from aiogram.dispatcher.filters import Filter
from models import get_user, get_step, get_all_locations


class Registered(Filter):

    async def check(self, msg: types.Message):
        if await get_user(msg.from_user.id):
            return True
        return False


class Step(Filter):

    def __init__(self, step):
        self.step = step

    async def check(self, msg: types.Message):
        if await get_step(msg) == self.step:
            return True
        return False


class HasLocations(Filter):

    async def check(self, msg: types.Message) -> bool:
        if await get_all_locations(msg.from_user.id):
            return True
        return False
