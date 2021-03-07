import logging

from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.utils.executor import start_webhook
from aiogram.utils import executor
from aiogram.types import ContentType

from models import *
from filters import Registered, Step, HasLocations
from utils import location_to_tuple
from gmap import find_near_locations

from config import (TOKEN, WEBHOOK_URL, WEBHOOK_PATH, WEBAPP_HOST, WEBAPP_PORT)

bot = Bot(TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())
new_locations = dict()


@dp.message_handler(~Registered(), commands=["start"])
async def process_start_command(message: types.Message):
    await create_user(message.from_user.id)
    await message.reply("Привет!"
                        "\nЯ сохраняю локации, чтобы не забыть про них. "
                        "\n/add, чтобы добавить место, "
                        "\n/list выведет 10 последних сохраненных мест, "
                        "\nты также можешь отправить локацию, чтобы получить все места в радиусе 500 метров. "
                        "\n/reset удалит все твои места, "
                        "\n/help для помощи, "
                        "\n/stop для остановки бота (удалит все ваши данные)")


@dp.message_handler(Registered(), commands=["start"])
async def already_started(message: types.Message):
    await bot.send_message(message.from_user.id, "Я уже запущен!")


@dp.message_handler(Registered(), commands=["help"])
async def process_help_command(message: types.Message):
    await message.reply("/add - добавить место\n"
                        "/list - список из 10 последних мест\n"
                        "Отправка локации - отобразить все места в радиусе 500 метров\n"
                        "/reset - удалить все локации\n"
                        "/stop - остановить бота, удалит все ваши данные\n"
                        "/help - показать эту справку\n")


@dp.message_handler(Registered(), commands=["stop"])
async def process_stop_command(message: types.Message):
    await delete_user(message.from_user.id)
    await message.reply("Пока!")


@dp.message_handler(Registered(), commands=["cancel"])
async def process_cancel_command(message: types.Message):
    id_ = message.from_user.id
    user_ = await get_user(id_)
    new_locations[id_] = dict()
    if user_.step != 0:
        user_.step = 0
        user_.save()
        await message.reply("Ввод места отменен.")


@dp.message_handler(Registered(), commands=["add"])
async def new_location(message: types.Message):
    id_ = message.from_user.id
    await next_step(id_)
    await bot.send_message(id_, "Введи описание места:\n/cancel для отмены")


@dp.message_handler(Registered(), HasLocations(), commands=["reset"])
async def delete_locations(message: types.Message):
    id_ = message.from_user.id
    await reset(id_)
    await bot.send_message(id_, "Все места удалены")


@dp.message_handler(Registered(), commands=["reset"])
async def delete_locations(message: types.Message):
    id_ = message.from_user.id
    await bot.send_message(id_, "У вас нет сохраненных мест")


@dp.message_handler(Registered(), Step(2), commands=["skip"])
async def skip_photo(message: types.Message):
    id_ = message.from_user.id
    await next_step(id_)
    await get_photo(message)


@dp.message_handler(Registered(), HasLocations(), Step(0), content_types=ContentType.LOCATION)
async def closest_locations(message: types.Message):
    id_ = message.from_user.id
    origin = await location_to_tuple(message)
    near_locations = await find_near_locations(id_, origin, 500)
    if near_locations:
        await bot.send_message(id_, "Ближайшие локации:")
        for location in near_locations:
            if location.pic:
                await bot.send_photo(id_, location.pic, location.name)
            else:
                await bot.send_message(id_, location.name)
            await bot.send_location(id_, location.x, location.y)
    else:
        await bot.send_message(id_, "Нет сохраненных мест поблизости"
                                    "\nЧтобы добавить место, используйте /add")


@dp.message_handler(Registered(), Step(0), content_types=ContentType.LOCATION)
async def no_locations(message: types.Message):
    id_ = message.from_user.id
    await bot.send_message(id_, "У вас нет сохраненных мест"
                                "\nЧтобы добавить место, используйте /add")


@dp.message_handler(Registered(), HasLocations(), commands=["list"])
async def list_of_locations(message: types.Message):
    id_ = message.from_user.id
    locations = await get_last_locations(id_)
    await bot.send_message(id_, "Ваши локации:")
    for location in locations:
        if location.pic:
            await bot.send_photo(id_, location.pic, location.name)
        else:
            await bot.send_message(id_, location.name)
        await bot.send_location(id_, location.x, location.y)


@dp.message_handler(Registered(), ~HasLocations(), commands=["list"])
async def list_but_no_locations(message: types.Message):
    id_ = message.from_user.id
    await bot.send_message(id_, "У вас нет сохраненных мест")


@dp.message_handler(Registered(), Step(1), content_types=ContentType.TEXT)
async def get_description(message: types.Message):
    id_ = message.from_user.id
    await next_step(id_)
    new_locations[id_] = dict()
    new_locations[id_]["text"] = message.text
    await bot.send_message(id_, "Теперь отправь локацию"
                                "\n/cancel для отмены")


@dp.message_handler(Registered(), Step(1))
async def no_description(message: types.Message):
    await message.reply("Пришли текстовое описание:"
                        "\n/cancel для отмены")


@dp.message_handler(Registered(), Step(2), content_types=ContentType.LOCATION)
async def get_location(message: types.Message):
    id_ = message.from_user.id
    await next_step(id_)
    new_locations[id_]["location"] = message.location
    await bot.send_message(id_, "Прикрепи фото (не обязательно):"
                                "\n/skip - пропустить"
                                "\n/cancel для отмены")


@dp.message_handler(Registered(), Step(2))
async def no_location(message: types.Message):
    id_ = message.from_user.id
    await bot.send_message(id_, "Отправь геопозицию (это обязательно):"
                                "\n/cancel для отмены")


@dp.message_handler(Registered(), Step(3))
async def get_photo(message: types.Message):
    id_ = message.from_user.id
    if message.photo:
        photo_path = f"{id_}.jpg"
        await message.photo[-1].download(photo_path)
        new_locations[id_]["photo"] = photo_path
    await send_location(id_)
    user_ = await get_user(id_)
    user_.step = 0
    user_.save()
    await bot.send_message(id_, "Место сохранено!")


@dp.message_handler(Registered())
async def default_message(message: types.Message):
    await bot.send_message(message.from_user.id, "/help для помощи")


async def send_location(id_):
    name = new_locations[id_]["text"]
    loc = new_locations[id_]["location"]
    pic = new_locations[id_].get("photo")
    await add_location(id_, name, loc, pic)
    new_locations[id_] = dict()
    if pic:
        os.remove(f"{id_}.jpg")


async def on_startup(dp_):
    await bot.set_webhook(WEBHOOK_URL)


async def on_shutdown(dp_):
    logging.warning('Shutting down..')
    await bot.delete_webhook()
    logging.warning('Bye!')


def main():
    if os.environ.get("DATABASE_URL"):
        logging.basicConfig(level=logging.INFO)
        start_webhook(
            dispatcher=dp,
            webhook_path=WEBHOOK_PATH,
            skip_updates=True,
            on_startup=on_startup,
            host=WEBAPP_HOST,
            port=WEBAPP_PORT,
        )
    else:
        try:
            executor.start_polling(dp)
        except KeyboardInterrupt:
            exit(0)


if __name__ == "__main__":
    main()
