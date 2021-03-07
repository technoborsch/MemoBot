import googlemaps
from models import get_all_locations

from config import MAPS_KEY

g_map = googlemaps.Client(MAPS_KEY)


async def find_near_locations(id_, origin_, distance: int):

    locations = await get_all_locations(id_)
    loc_tuples = [(loc.x, loc.y) for loc in locations]
    data = googlemaps.client.distance_matrix(g_map, origin_, loc_tuples)
    distances = [elem["distance"]["value"] for elem in data["rows"][0]["elements"]]
    near_locations = [loc[1] for loc in enumerate(locations) if distances[loc[0]] < distance]
    return near_locations
