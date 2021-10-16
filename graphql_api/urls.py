from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from graphene_django.views import GraphQLView
from graphql_jwt.decorators import jwt_cookie
from graphql_playground.views import GraphQLPlaygroundView

from work_around.settings import DEBUG

urlpatterns = [
    path("", csrf_exempt(jwt_cookie(GraphQLView.as_view(graphiql=True)))),
]

if DEBUG:
    urlpatterns.append(
        path('playground/', GraphQLPlaygroundView.as_view(endpoint="http://localhost:8000/graphql/"))
    )
