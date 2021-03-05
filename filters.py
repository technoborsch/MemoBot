from aiogram.dispatcher.filters import Filter
from aiogram import types
from models import get_user, get_step


class Registered(Filter):

    async def check(self, msg: types.Message, *args) -> bool:
        if await get_user(msg.from_user.id):
            return True
        return False


class Step(Filter):

    def __init__(self, step):
        self.step = step

    async def check(self, msg: types.Message, *args) -> bool:
        if await get_step(msg) == self.step:
            return True
        return False
