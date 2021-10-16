import graphene
from django.contrib.auth.models import User
from graphene import ObjectType
from graphene_django import DjangoObjectType


class HealthType(ObjectType):
    running = graphene.Boolean(required=True)


class UserType(DjangoObjectType):
    class Meta:
        model = User
        exclude = ("password",)


class Query(graphene.ObjectType):
    health = graphene.Field(HealthType, required=True)
    users = graphene.List(graphene.NonNull(UserType), required=True)

    @staticmethod
    def resolve_health(root, info):
        return HealthType(running=True)

    @staticmethod
    def resolve_users(root, info):
        return User.objects.all()


schema = graphene.Schema(query=Query)
