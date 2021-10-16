import graphene
from django.contrib.gis.db import models
from django.contrib.gis.db.models.functions import Distance
from graphene import Field, Mutation, Boolean, String, Int, Float, ID, List
from graphene_django import DjangoObjectType
from graphene_django.converter import convert_django_field
from graphene_django.debug import DjangoDebug
from opencage.geocoder import OpenCageGeocode

from graphql_api.models import User, Property, LifestyleType, FacilityType, LengthOfStay, RoomType, City, PropertyType
from graphql_api.utils import GeographyPoint
from work_around import settings

geocoder = OpenCageGeocode(settings.OPEN_CAGE_API_KEY)


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


class LifestyleTypeType(DjangoObjectType):
    class Meta:
        model = LifestyleType


class FacilityTypeType(DjangoObjectType):
    class Meta:
        model = FacilityType


class PropertyTypeType(DjangoObjectType):
    class Meta:
        model = PropertyType


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
    lifestyle_types = graphene.List(graphene.NonNull(LifestyleTypeType), required=True)
    facility_types = graphene.List(graphene.NonNull(FacilityTypeType), required=True)
    property_types = graphene.List(graphene.NonNull(PropertyTypeType), required=True)
    lengths_of_stay = graphene.List(graphene.NonNull(Int), required=True)
    room_types = graphene.List(graphene.NonNull(String), required=True)

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

    @staticmethod
    def resolve_lifestyle_types(root, info):
        return LifestyleType.objects.all()

    @staticmethod
    def resolve_facility_types(root, info):
        return FacilityType.objects.all()

    @staticmethod
    def resolve_property_types(root, info):
        return PropertyType.objects.all()

    @staticmethod
    def resolve_lengths_of_stay(root, info):
        return [e.value for e in LengthOfStay]

    @staticmethod
    def resolve_room_types(root, info):
        return [e.value for e in RoomType]


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


class CreateProperty(Mutation, SuccessMixin):
    class Arguments:
        name = String(required=True)
        description = String()
        coordinates = PointInputType(required=True)
        user_id = Int(required=True)
        usd_worth = Float(required=True)

    created_property = graphene.NonNull(PropertyType)

    def mutate(parent, info, coordinates, **kwargs):
        geocoder_result = geocoder.reverse_geocode(coordinates.x, coordinates.y)
        city = City.objects.get_or_create(name=geocoder_result["city"], country=geocoder_result["country"])
        return CreateProperty(created_property=Property.objects.create(**kwargs, coordinates=coordinates, city=city))


class UpdateProperty(Mutation, SuccessMixin):
    class Arguments:
        property_id = Int(required=True)
        name = String()
        description = String()
        coordinates = PointInputType()
        user_id = Int()
        is_available = Boolean()
        usd_worth = Float()

    property = Field(PropertyType)

    def mutate(parent, info, property_id, coordinates=None, **kwargs):
        property_queryset = Property.objects.filter(id=property_id)
        if coordinates is not None:
            geocoder_result = geocoder.reverse_geocode(coordinates.x, coordinates.y)
            city = City.objects.get_or_create(name=geocoder_result["city"], country=geocoder_result["country"])
            kwargs.update(coordinates=coordinates, city=city)

        property_queryset.update(**{key: value for key, value in kwargs.values() if value is not None})
        return UpdateProperty(property=property_queryset.get())


class CreateProperty(Mutation, SuccessMixin):
    class Arguments:
        coordinates = PointInputType()
        user_id = Int()
        name = String()
        description = String()
        is_available = Boolean()
        usd_worth = Float()
        photo_id = Int()
        meters_squared = Float()
        property_type = ID()
        room_type = String()
        facility_types = List(ID)
        lifestyle_types = List(ID)

    property = Field(PropertyType)

    def mutate(parent, info, **kwargs):
        property = Property(**kwargs)
        property.save()
        return CreateProperty(property=property)


class Login(graphene.Mutation, SuccessMixin):
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


class Register(graphene.Mutation, SuccessMixin):
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
    create_property = CreateProperty.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
