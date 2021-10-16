import graphene
from django.contrib.gis.db import models
from django.contrib.gis.db.models.functions import Distance
from graphene import Field, Mutation, Boolean, String, Int, Float
from graphene_django import DjangoObjectType
from graphene_django.converter import convert_django_field
from graphene_django.debug import DjangoDebug

from graphql_api.models import User, Property
from graphql_api.utils import GeographyPoint
from work_around import settings


class PointTypeMixin:
    x = graphene.Float(required=True)
    y = graphene.Float(required=True)

    def get_point(self):
        return GeographyPoint(self.x, self.y)


class PointType(graphene.ObjectType, PointTypeMixin):
    pass


class PointInputType(graphene.InputObjectType, PointTypeMixin):
    pass


@convert_django_field.register(models.PointField)
def convert_point_field_to_type(field, registry=None):
    return graphene.Field(
        PointType,
        description=field.help_text,
        required=not field.null
    )


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
                                       coordinates=PointInputType(),
                                       max_distance=graphene.Float(description="Maximal distance in kilometers"),
                                       is_available=graphene.Boolean())

    @staticmethod
    def resolve_health(root, info):
        return HealthType(running=True)

    @staticmethod
    def resolve_users(root, info):
        return User.objects.all()

    @staticmethod
    def resolve_closest_properties(root, info, coordinates: PointInputType = None, max_distance: float = None,
                                   is_available: bool = None):

        coordinates = GeographyPoint(x=50.083076, y=14.420020) if coordinates is None else coordinates.get_point()
        properties = Property.objects.annotate(distance=Distance('coordinates', coordinates)) \
            .order_by('distance')
        if max_distance is not None:
            properties = properties.filter(distance__lte=max_distance * 1000)
        if is_available is not None:
            properties = properties.filter(is_available=is_available)
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
        coordinates = PointInputType()
        user_id = Int()
        is_available = Boolean()
        usd_worth = Float()

    property = Field(PropertyType)

    def mutate(parent, info, property_id, coordinates=None, user_id=None, is_available=None, usd_worth=None):
        property = Property.objects.get(id=property_id)
        if coordinates: property.coordinates = coordinates.get_point()
        if user_id: property.user_id = user_id
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
        user = User.objects.get(email=email)
        if not user.check_password(password):
            raise Exception("Wrong password.")
        return Login(me=user)


class Register(graphene.Mutation):
    class Arguments:
        username = graphene.String(required=True)
        email = graphene.String(required=True)
        password = graphene.String(required=True)

    me = graphene.NonNull(UserType)

    @staticmethod
    def mutate(root, info, username, email, password):
        return Register(me=User.objects.create_user(username=username, email=email, password=password))


class Mutation(graphene.ObjectType):
    debug = graphene.Field(DjangoDebug, name='_debug') if settings.DEBUG else None
    register = Register.Field()
    login = Login.Field()
    update_user = UpdateUser.Field()
    update_property = UpdateProperty.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
