import datetime
from peewee import *

db = SqliteDatabase("db", pragmas={'foreign_keys': 'on'})
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


class Location(BaseModel):
    """Сохраненные локации"""
    id = AutoField(column_name="id")
    user = ForeignKeyField(User, column_name="user", backref="locations", on_delete="CASCADE")
    name = TextField(column_name="name")
    x = DecimalField(column_name="x")
    y = DecimalField(column_name="y")
    pic = BlobField(column_name="pic", null=True)
    time = TimeField(column_name="date")


def get_user(tg_id):
    return User.get(tg_id=tg_id)


def create_user(tg_id):
    if not User.filter(tg_id=tg_id):
        date = today()
        User.create(tg_id=tg_id, join_date=date)
        return True
    return False


def delete_user(tg_id):
    try:
        user_ = get_user(tg_id)
        user_.delete_instance()
        return True
    except DoesNotExist:
        return False


def add_location(tg_id, name, location, pic=None):
    user_ = get_user(tg_id)
    time = now()
    x = location["latitude"]
    y = location["longitude"]
    if pic:
        pic = open(pic, "rb").read()
    Location.create(user=user_, name=name, x=x, y=y, pic=pic, time=time)
    return True


def get_last_locations(tg_id):
    user_ = get_user(tg_id)
    return Location.select().where(Location.user == user_.id).order_by(Location.id.desc()).limit(10)


def get_all_locations(tg_id):
    user_ = get_user(tg_id)
    return Location.select().where(Location.user == user_.id).order_by(Location.id.desc())


def delete_location(tg_id, name):
    try:
        user_id = User.get(tg_id=tg_id).user_id
        loc = Location.get(user_id=user_id, name=name)
        loc.delete_instance()
        return True
    except DoesNotExist:
        return False


def reset(tg_id):
    user_ = get_user(tg_id)
    if len(user_.locations) > 0:
        for location in user_.locations:
            location.delete_instance()
            return True
    return False


def get_step(msg):
    return User.get(tg_id=msg.from_user.id).step


def next_step(id_):
    usr = User.get(tg_id=id_)
    usr.step += 1
    usr.save()


db.connect()
db.create_tables([User, Location])
db.close()


def main():
    print(list(get_last_locations(1339992910)))


if __name__ == "__main__":
    main()
