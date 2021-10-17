import logging
from typing import Tuple

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
    geocoder_result = geocoder.reverse_geocode(coordinates.x, coordinates.y)[0]["components"]
    try:
        city_name = geocoder_result.get("city",
                                        geocoder_result.get("suburb",
                                                            geocoder_result.get("county")))
        city_name = city_name or geocoder_result["region"]
        city, _ = City.objects.get_or_create(name=city_name, country=geocoder_result["country"])
    except KeyError as e:
        logger.exception(e)
        return None
    return city

