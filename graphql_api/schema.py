import json

import graphene
from django.contrib.gis.db import models
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import Point
from graphene_django import DjangoObjectType
from graphene_django.converter import convert_django_field
from graphene_django.debug import DjangoDebug

from graphql_api.models import User, Property
from work_around import settings


class GeoJSON(graphene.Scalar):
    @classmethod
    def serialize(cls, value):
        return json.loads(value.geojson)


@convert_django_field.register(models.GeometryField)
def convert_field_to_geojson(field, registry=None):
    return graphene.Field(
        GeoJSON,
        description=field.help_text,
        required=not field.null)


class HealthType(graphene.ObjectType):
    running = graphene.Boolean(required=True)


class UserType(DjangoObjectType):
    class Meta:
        model = User
        exclude = ("password",)


class PropertyType(DjangoObjectType):
    class Meta:
        model = Property


class Query(graphene.ObjectType):
    debug = graphene.Field(DjangoDebug, name='_debug') if settings.DEBUG else None
    health = graphene.Field(HealthType, required=True)
    users = graphene.List(graphene.NonNull(UserType), required=True)
    closest_properties = graphene.List(graphene.NonNull(PropertyType), required=True,
                                       lat=graphene.Float(required=True), lng=graphene.Float(required=True),
                                       max_distance=graphene.Float(description="Maximal distance in kilometers"))

    @staticmethod
    def resolve_health(root, info):
        return HealthType(running=True)

    @staticmethod
    def resolve_users(root, info):
        return User.objects.all()

    @staticmethod
    def resolve_closest_properties(root, info, lat: float, lng: float, max_distance: float = None):
        properties = Property.objects.annotate(distance=Distance('coordinates', Point(lat, lng, srid=4326)))\
            .order_by('distance')
        if max_distance is not None:
            properties = properties.filter(distance__lte=max_distance*1000)
        return properties


class Mutation(graphene.ObjectType):
    debug = graphene.Field(DjangoDebug, name='_debug') if settings.DEBUG else None
    pass


schema = graphene.Schema(query=Query, mutation=Mutation)
