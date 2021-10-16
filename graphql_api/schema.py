import json

import graphene
from django.contrib.gis.db import models
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import Point
from graphene_django import DjangoObjectType
from graphene_django.converter import convert_django_field

from graphql_api.models import User, Property


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
    debug = Field(DjangoDebug, name='_debug') if settings.DEBUG else None
    health = graphene.Field(HealthType, required=True)
    users = graphene.List(graphene.NonNull(UserType), required=True)

    @staticmethod
    def resolve_health(root, info):
        return HealthType(running=True)

    @staticmethod
    def resolve_users(root, info):
        return User.objects.all()


class Mutation:
    debug = Field(DjangoDebug, name='_debug') if settings.DEBUG else None
    pass


schema = graphene.Schema(query=Query, mutation=Mutation)
