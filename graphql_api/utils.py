import logging
from typing import Tuple
import itertools

from django.contrib.gis.geos import Point
from opencage.geocoder import OpenCageGeocode

from work_around import settings

logger = logging.getLogger(__name__)


class GeographyPoint(Point):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, srid=4326)


geocoder = OpenCageGeocode(settings.OPEN_CAGE_API_KEY)


def get_city(coordinates):
    from graphql_api.models import City
    place_components = geocoder.reverse_geocode(coordinates.x, coordinates.y)[0]
    city_coordinates = place_components["geometry"]
    place_components = place_components["components"]
    try:
        city_name = place_components.get("city",
                                         place_components.get("suburb",
                                                              place_components.get("county")))
        city_name = city_name or place_components["region"]
        city, _ = City.objects.get_or_create(name=city_name, country=place_components["country"])
    except KeyError as e:
        logger.exception(e)
        return None
    return city


def pairwise(iterable):
    a, b = itertools.tee(iterable)
    first = next(b, None)
    return zip(a, b)
