import datetime
import os
from urllib.parse import urlparse
from peewee import *

if os.environ.get("DATABASE_URL"):
    DATABASE_URL = os.environ.get("DATABASE_URL")
    dbase = urlparse(DATABASE_URL)
    user = dbase.username
    password = dbase.password
    path = dbase.path[1:]
    host = dbase.hostname
    port = dbase.port
    db = PostgresqlDatabase(path, user=user, password=password, host=host, port=port)
else:
    db = PostgresqlDatabase("memobot", user="postgres", password="BetteRlifE4uS", host="127.0.0.1", port="5432")

today = datetime.date.today
now = datetime.datetime.now


class BaseModel(Model):
    class Meta:
        database = db


class User(BaseModel):
    """Информация о пользователе"""
    id = AutoField(column_name="id")
    tg_id = CharField(column_name="tg_id", unique=True)
    join_date = DateField(column_name="join_date")
    step = IntegerField(column_name="step", default=0)

    class Meta:
        db_table = 'users'


class Location(BaseModel):
    """Сохраненные локации"""
    id = AutoField(column_name="id")
    user = ForeignKeyField(User, column_name="user", backref="locations", on_delete="CASCADE")
    name = TextField(column_name="name")
    x = DecimalField(column_name="x")
    y = DecimalField(column_name="y")
    pic = BlobField(column_name="pic", null=True)
    time = TimeField(column_name="date")


async def get_user(tg_id):
    return await User.get(tg_id=tg_id)


async def create_user(tg_id):
    if not await User.filter(tg_id=tg_id):
        date = today()
        await User.create(tg_id=tg_id, join_date=date)
        return True
    return False


async def delete_user(tg_id):
    user_ = await get_user(tg_id)
    await user_.delete_instance
    return True


async def add_location(tg_id, name, location, pic=None):
    time = now()
    x = location["latitude"]
    y = location["longitude"]
    if pic:
        async with open(pic, "rb") as f:
            await Location.create(user=get_user(tg_id), name=name, x=x, y=y, pic=f.read(), time=time)
    await Location.create(user=get_user(tg_id), name=name, x=x, y=y, pic=pic, time=time)
    return True


async def get_last_locations(tg_id):
    user_ = await get_user(tg_id)
    return await Location.select().where(Location.user == user_.id).order_by(Location.id.desc()).limit(10)


async def get_all_locations(tg_id):
    user_ = await get_user(tg_id)
    return await Location.select().where(Location.user == user_.id).order_by(Location.id.desc())


async def delete_location(tg_id, name):
    try:
        user_ = await get_user(tg_id)
        loc = await Location.get(user_id=user_.user_id, name=name)
        await loc.delete_instance()
        return True
    except DoesNotExist:
        return False


async def reset(tg_id):
    user_ = await get_user(tg_id)
    if len(user_.locations) > 0:
        async for location in user_.locations:
            await location.delete_instance()
            return True
    return False


async def get_step(msg):
    return await User.get(tg_id=msg.from_user.id).step


async def next_step(id_):
    usr = await User.get(tg_id=id_)
    usr.step += 1
    await usr.save()


db.connect()
db.create_tables([User, Location])
db.close()


def main():
    pass


if __name__ == "__main__":
    main()
