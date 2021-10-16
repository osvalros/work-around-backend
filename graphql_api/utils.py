from django.contrib.gis.geos import Point


class GeographyPoint(Point):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, srid=4326)


