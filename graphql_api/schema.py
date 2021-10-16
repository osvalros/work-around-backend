import json

import graphene
from django.contrib.gis.db import models
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import Point
from django.contrib.auth.models import User
from graphene import ObjectType, Field, Mutation, Boolean, String, Int, Float
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
    distance = graphene.Float(required=False, description="Distance from queried value (if queried) in kilometers.")

    @staticmethod
    def resolve_distance(parent, info):
        if not hasattr(parent, "distance"):
            return None
        return parent.distance.m / 1000

    class Meta:
        model = Property


class Query(graphene.ObjectType):
    debug = graphene.Field(DjangoDebug, name='_debug') if settings.DEBUG else None
    health = graphene.Field(HealthType, required=True)
    users = graphene.List(graphene.NonNull(UserType), required=True)
    closest_properties = graphene.List(graphene.NonNull(PropertyType), required=True,
                                       lat=graphene.Float(default_value=50.083076), lng=graphene.Float(default_value=14.420020),
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


class SuccessMixin:
    success = Boolean(required=True)

    def resolve_success(parent, info):
        return parent.success if parent.success is not None else True


class UpdateUser(Mutation, SuccessMixin):
    class Arguments:
        user_id = Int(required=True)
        first_name = String()
        last_name = String()

    user = Field(UserType)

    def mutate(parent, info, user_id, first_name=None, last_name=None):
        user = User.objects.get(id=user_id)
        if first_name: user.first_name = first_name
        if last_name: user.last_name = last_name
        user.save()
        return UpdateUser(user=user)


class UpdateProperty(Mutation, SuccessMixin):
    class Arguments:
        property_id = Int(required=True)
        coordinates = GeoJSON()
        user = Int()
        is_available = Boolean()
        usd_worth = Float()

    property = Field(PropertyType)

    def mutate(parent, info, property_id, coordinates=None, user=None, is_available=None, usd_worth=None):
        property = Property.objects.get(id=property_id)
        if coordinates: property.coordinates = coordinates
        if user: property.user = user
        if is_available: property.is_available = is_available
        if usd_worth: property.usd_worth = usd_worth
        property.save()
        return UpdateProperty(property=property)


class Login(graphene.Mutation):
    class Arguments:
        email = graphene.String(required=True)
        password = graphene.String(required=True)

    me = graphene.NonNull(UserType)

    @staticmethod
    def mutate(root, info, email, password):
        return Login(me=User.objects.get(email=email))


class Register(graphene.Mutation):
    class Arguments:
        username = graphene.String(required=True)
        email = graphene.String(required=True)
        password = graphene.String(required=True)

    me = graphene.NonNull(UserType)

    @staticmethod
    def mutate(root, info, username, email, password):
        return User.objects.create_user(username=username, email=email, password=password)


class Mutation(graphene.ObjectType):
    debug = graphene.Field(DjangoDebug, name='_debug') if settings.DEBUG else None
    register = Register.Field()
    login = Login.Field()
    update_user = UpdateUser.Field()
    update_property = UpdateProperty.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
