from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.types import ContentType
import googlemaps
from models import *
import os

from config import TOKEN, MAPS_KEY

bot = Bot(TOKEN)
dp = Dispatcher(bot)
new_locations = dict()
g_map = googlemaps.Client(MAPS_KEY)


@dp.message_handler(commands=["start"])
async def process_start_command(message: types.Message):
    if not User.filter(tg_id=message.from_user.id):
        create_user(message.from_user.id)
        await message.reply("Привет!"
                            "\nЯ сохраняю локации, чтобы не забыть про них. "
                            "\n/add, чтобы добавить место, "
                            "\n/list выведет 10 последних сохраненных мест, "
                            "\nты также можешь отправить локацию, чтобы получить все места в радиусе 500 метров. "
                            "\n/reset удалит все твои места, "
                            "\n/help для помощи, "
                            "\n/stop для остановки бота (удалит все ваши данные)")
    else:
        await message.reply("Я уже запущен!")


@dp.message_handler(commands=["help"])
async def process_help_command(message: types.Message):
    await message.reply("/add - добавить место\n"
                        "/list - список из 10 последних мест\n"
                        "Отправка локации - отобразить все места в радиусе 500 метров\n"
                        "/reset - удалить все локации\n"
                        "/stop - остановить бота, удалит все ваши данные\n"
                        "/help - показать эту справку\n")


@dp.message_handler(commands=["stop"])
async def process_stop_command(message: types.Message):
    delete_user(message.from_user.id)
    await message.reply("Пока!")


@dp.message_handler(commands=["cancel"])
async def process_cancel_command(message: types.Message):
    id_ = message.from_user.id
    user = get_user(id_)
    new_locations[id_] = dict()
    if user.step != 0:
        user.step = 0
        user.save()
        await message.reply("Ввод места отменен.")


@dp.message_handler(commands=["add"])
async def new_location(message: types.Message):
    id_ = message.from_user.id
    next_step(id_)
    await bot.send_message(id_, "Введи описание места:\n/cancel для отмены")


@dp.message_handler(commands=["reset"])
async def delete_locations(message: types.Message):
    id_ = message.from_user.id
    if reset(id_):
        await bot.send_message(id_, "Все места удалены")
    else:
        await bot.send_message(id_, "У вас нет сохраненных мест")


@dp.message_handler(lambda m: get_step(m) == 2, commands=["skip"])
async def skip_photo(message: types.Message):
    id_ = message.from_user.id
    next_step(id_)
    await get_photo(message)


@dp.message_handler(lambda m: get_step(m) == 0, content_types=ContentType.LOCATION)
async def nearest_locations(message: types.Message):
    id_ = message.from_user.id
    locations = get_all_locations(id_)
    if locations:
        loc_tuples = [(loc.x, loc.y) for loc in locations]
        origin = (message.location["latitude"], message.location["longitude"])
        data = googlemaps.client.distance_matrix(g_map, origin, loc_tuples)
        distances = [elem["distance"]["value"] for elem in data["rows"][0]["elements"]]
        near_locs = [loc[1] for loc in enumerate(locations) if distances[loc[0]] < 500]
        if near_locs:
            await bot.send_message(id_, "Ближайшие локации:")
            for location in near_locs:
                if location.pic:
                    await bot.send_photo(id_, location.pic, location.name)
                else:
                    await bot.send_message(id_, location.name)
                await bot.send_location(id_, location.x, location.y)
        else:
            await bot.send_message(id_, "Нет сохраненных мест поблизости"
                                        "\nЧтобы добавить место, используйте /add")
    else:
        await bot.send_message(id_, "У вас нет сохраненных мест"
                                    "\nЧтобы добавить место, используйте /add")


@dp.message_handler(commands=["list"])
async def list_of_locations(message: types.Message):
    id_ = message.from_user.id
    locations = get_last_locations(id_)
    if locations:
        await bot.send_message(id_, "Ваши локации:")
        for location in locations:
            if location.pic:
                await bot.send_photo(id_, location.pic, location.name)
            else:
                await bot.send_message(id_, location.name)
            await bot.send_location(id_, location.x, location.y)
    else:
        await bot.send_message(id_, "У вас нет сохраненных мест")


@dp.message_handler(lambda m: get_step(m) == 1)
async def get_description(message: types.Message):
    id_ = message.from_user.id
    if message.text:
        next_step(id_)
        new_locations[id_] = dict()
        new_locations[id_]["text"] = message.text
        await bot.send_message(id_, "Отлично! Теперь отправь локацию"
                                    "\n/cancel для отмены")
    else:
        await message.reply("Пришли текстовое описание:"
                            "\n/cancel для отмены")


@dp.message_handler(lambda m: get_step(m) == 2, content_types=ContentType.LOCATION)
async def get_location(message: types.Message):
    id_ = message.from_user.id
    next_step(id_)
    new_locations[id_]["location"] = message.location
    await bot.send_message(id_, "Прикрепи фото (не обязательно):"
                                "\n/skip - пропустить"
                                "\n/cancel для отмены")


@dp.message_handler(lambda m: get_step(m) == 2)
async def no_location(message: types.Message):
    id_ = message.from_user.id
    await bot.send_message(id_, "Отправь геопозицию (это обязательно):"
                                "\n/cancel для отмены")


@dp.message_handler(lambda m: get_step(m) == 3, content_types=[ContentType.ANY])
async def get_photo(message: types.Message):
    id_ = message.from_user.id
    if message.photo:
        photo_path = f"{id_}.jpg"
        await message.photo[-1].download(photo_path)
        new_locations[id_]["photo"] = photo_path
    send_location(id_)
    user_ = get_user(id_)
    user_.step = 0
    user_.save()
    await bot.send_message(id_, "Место сохранено!")


@dp.message_handler()
async def default_message(message: types.Message):
    await bot.send_message(message.from_user.id, "/help для помощи")


def send_location(id_):
    name = new_locations[id_]["text"]
    loc = new_locations[id_]["location"]
    pic = new_locations[id_].get("photo")
    add_location(id_, name, loc, pic)
    new_locations[id_] = dict()
    if pic:
        os.remove(f"{id_}.jpg")


if __name__ == '__main__':
    try:
        executor.start_polling(dp)
    except KeyboardInterrupt:
        exit(0)