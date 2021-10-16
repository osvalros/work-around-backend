import graphene
from graphene import Field
from graphene import ObjectType
from graphene_django import DjangoObjectType
from graphene_django.debug import DjangoDebug

from graphql_api.models import User
from work_around import settings


class HealthType(ObjectType):
    running = graphene.Boolean(required=True)


class UserType(DjangoObjectType):
    class Meta:
        model = User
        exclude = ("password",)


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
