async def location_to_tuple(msg) -> tuple:
    if msg.location:
        return msg.location["latitude"], msg.location["longitude"]


async def render_locations(id_):
    pass
