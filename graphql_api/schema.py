import typing

import graphene
from dateutil.parser import isoparse
from django.contrib.gis.db import models
from django.contrib.gis.db.models.functions import Distance
from django.db import transaction
from graphene import Field, Mutation, Boolean, String, Int, Float, ID, List
from graphene_django import DjangoObjectType
from graphene_django.converter import convert_django_field
from graphene_django.debug import DjangoDebug

from graphql_api.matching import MatchingAlgorithm
from graphql_api.models import User, Property, LifestyleType, FacilityType, LengthOfStay, RoomType, City, PropertyType, \
    Application, CommuteType, ApplicationPreferredCity, RecommendationApplication, Recommendation
from graphql_api.utils import GeographyPoint, get_city
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


class ApplicationType(DjangoObjectType):
    length_of_stay = graphene.String()

    @staticmethod
    def resolve_length_of_stay(parent: Application, info):
        return f"{parent.length_of_stay} months"

    class Meta:
        model = Application


class ProgressType(graphene.ObjectType):
    done = graphene.Int()
    total = graphene.Int()


class RecommendationType(DjangoObjectType):
    progress = graphene.NonNull(ProgressType)

    @staticmethod
    def resolve_progress(parent: Recommendation, info):
        done = parent.recommendation_applications.filter(accepted=True).count()
        total = parent.recommendation_applications.count()
        return ProgressType(done=done, total=total)

    class Meta:
        model = Recommendation


class RecommendationApplicationType(DjangoObjectType):
    class Meta:
        model = RecommendationApplication


class UserType(DjangoObjectType):
    applications = graphene.List(graphene.NonNull(lambda: ApplicationType))

    @staticmethod
    def resolve_applications(parent: User, info):
        return Application.objects.filter(property__user=parent)

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


class CommuteTypeType(DjangoObjectType):
    class Meta:
        model = CommuteType


class PropertyObjectType(DjangoObjectType):
    room_type = graphene.String()
    distance = graphene.Float(required=False, description="Distance from queried value (if queried) in kilometers.")

    @staticmethod
    def resolve_room_type(parent: Property, info):
        return parent.room_type

    @staticmethod
    def resolve_distance(parent, info):
        if not hasattr(parent, "distance"):
            return None
        return parent.distance.m / 1000

    class Meta:
        model = Property


class CityType(DjangoObjectType):
    class Meta:
        model = City


class Query(graphene.ObjectType):
    debug = graphene.Field(DjangoDebug, name='_debug') if settings.DEBUG else None
    health = graphene.Field(HealthType, required=True)
    users = graphene.List(graphene.NonNull(UserType), required=True)
    applications = graphene.List(graphene.NonNull(ApplicationType), required=True, user_id=Int())
    closest_properties = graphene.List(graphene.NonNull(PropertyObjectType), required=True,
                                       coordinates=PointInputType(),
                                       max_distance=graphene.Float(description="Maximal distance in kilometers"),
                                       is_available=graphene.Boolean())
    lifestyle_types = graphene.List(graphene.NonNull(LifestyleTypeType), required=True)
    facility_types = graphene.List(graphene.NonNull(FacilityTypeType), required=True)
    property_types = graphene.List(graphene.NonNull(PropertyTypeType), required=True)
    commute_types = graphene.List(graphene.NonNull(CommuteTypeType), required=True)
    lengths_of_stay = graphene.List(graphene.NonNull(Int), required=True)
    room_types = graphene.List(graphene.NonNull(String), required=True)
    available_cities = graphene.List(graphene.NonNull(CityType))
    recommended_applications = graphene.List(graphene.NonNull(RecommendationApplicationType), required=True,
                                             user_id=ID(required=True))

    @staticmethod
    def resolve_health(root, info):
        return HealthType(running=True)

    @staticmethod
    def resolve_users(root, info):
        return User.objects.all()

    @staticmethod
    def resolve_applications(root, info, user_id: Int):
        return Application.objects.filter(property__user_id=user_id).all()

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
    def resolve_commute_types(root, info):
        return CommuteType.objects.all()

    @staticmethod
    def resolve_lengths_of_stay(root, info):
        return [e.value for e in LengthOfStay]

    @staticmethod
    def resolve_room_types(root, info):
        return [e.value for e in RoomType]

    @staticmethod
    def resolve_available_cities(root, info):
        return City.objects.filter(properties__is_available=True).distinct()

    @staticmethod
    def resolve_recommended_applications(root, info, user_id: str):
        recommendation_applications = RecommendationApplication.objects \
            .filter(application__property__user_id=user_id) \
            .prefetch_related("recommended", "recommended__application")
        return {recommendation_application.recommended.application_id: recommendation_application.recommended
                for recommendation_application in recommendation_applications}.values()


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
        user_id = ID(required=True)
        number_of_people = Int()
        usd_worth = Float(required=True)
        photo_id = String(required=True)
        meters_squared = Int(required=True)
        property_type_id = ID(required=True)
        room_type = String(required=True)
        facility_type_ids = List(graphene.NonNull(ID), required=True)
        lifestyle_type_ids = List(graphene.NonNull(ID), required=True)

    created_property = graphene.NonNull(PropertyObjectType)

    @staticmethod
    @transaction.atomic
    def mutate(root, info, coordinates, facility_type_ids: typing.List[str], lifestyle_type_ids: typing.List[str],
               **kwargs):
        facility_types = FacilityType.objects.filter(id__in=facility_type_ids)
        lifestyle_types = LifestyleType.objects.filter(id__in=lifestyle_type_ids)
        created_property = Property.objects.create(**kwargs, coordinates=coordinates.get_point(),
                                                   city=get_city(coordinates))
        created_property.facility_types.set(facility_types)
        created_property.lifestyle_types.set(lifestyle_types)
        return CreateProperty(created_property=created_property)


class UpdateProperty(Mutation, SuccessMixin):
    class Arguments:
        property_id = Int(required=True)
        name = String()
        description = String()
        coordinates = PointInputType()
        user_id = Int()
        is_available = Boolean()
        usd_worth = Float()

    property = Field(PropertyObjectType)

    @staticmethod
    @transaction.atomic
    def mutate(root, info, property_id, coordinates=None, **kwargs):
        property_queryset = Property.objects.filter(id=property_id)
        if coordinates is not None:
            kwargs.update(coordinates=coordinates.get_point(), city=get_city(coordinates))

        property_queryset.update(**{key: value for key, value in kwargs.values() if value is not None})
        return UpdateProperty(property=property_queryset.get())


class DeleteProperty(Mutation, SuccessMixin):
    class Arguments:
        property_id = graphene.ID(required=True)

    @staticmethod
    def mutate(root, info, property_id):
        Property.objects.get(id=property_id).delete()
        return DeleteProperty()


class CreateApplication(Mutation, SuccessMixin):
    class Arguments:
        property_id = ID(required=True)
        length_of_stay = Int(required=True)
        move_in_date = String(required=True)  # using date because of frontend code generation problem
        pet_friendly = Boolean(required=True)
        preferred_cities_ids = graphene.List(graphene.NonNull(ID), required=True)
        lifestyle_types_ids = graphene.List(graphene.NonNull(ID), required=True)
        commute_types_ids = graphene.List(graphene.NonNull(ID), required=True)
        property_types_ids = graphene.List(graphene.NonNull(ID), required=True)
        facility_types_ids = graphene.List(graphene.NonNull(ID), required=True)

    created_application = Field(ApplicationType)

    @staticmethod
    @transaction.atomic
    def mutate(parent, info, move_in_date: str,
               preferred_cities_ids: typing.List[str],
               lifestyle_types_ids: typing.List[str],
               commute_types_ids: typing.List[str],
               property_types_ids: typing.List[str],
               facility_types_ids: typing.List[str],
               **kwargs):
        created_application = Application.objects.create(**kwargs,
                                                         move_in_date=isoparse(move_in_date))
        ApplicationPreferredCity.objects.bulk_create(
            [ApplicationPreferredCity(application=created_application, city_id=preferred_city_id, order=index + 1)
             for index, preferred_city_id in enumerate(preferred_cities_ids)]
        )
        created_application.lifestyle_types.set(LifestyleType.objects.filter(id__in=lifestyle_types_ids))
        created_application.commute_types.set(CommuteType.objects.filter(id__in=commute_types_ids))
        created_application.property_types.set(PropertyType.objects.filter(id__in=property_types_ids))
        created_application.facility_types.set(FacilityType.objects.filter(id__in=facility_types_ids))

        Recommendation.objects.filter(accepted=False).delete()

        for application_ids in MatchingAlgorithm().find_matching_application_sets():
            Recommendation.objects.create_recommendation(application_ids)

        return CreateApplication(created_application=created_application)


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


class AcceptRecommendation(graphene.Mutation, SuccessMixin):
    class Arguments:
        recommendation_application_id = graphene.ID(required=True)

    recommendation_application = graphene.NonNull(RecommendationApplicationType)

    @staticmethod
    def mutate(root, info, recommendation_application_id: str):
        recommendation_application = \
            RecommendationApplication.objects.get(id=recommendation_application_id)
        recommendation_application.accept()
        return AcceptRecommendation(recommendation_application=recommendation_application)


class Mutation(graphene.ObjectType):
    debug = graphene.Field(DjangoDebug, name='_debug') if settings.DEBUG else None
    register = Register.Field()
    login = Login.Field()
    update_user = UpdateUser.Field()
    update_property = UpdateProperty.Field()
    create_property = CreateProperty.Field()
    delete_property = DeleteProperty.Field()
    create_application = CreateApplication.Field()
    accept_recommendation = AcceptRecommendation.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
