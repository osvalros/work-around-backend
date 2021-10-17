from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from graphql_jwt.decorators import jwt_cookie
from graphql_playground.views import GraphQLPlaygroundView

from graphql_api.views import WorkAroundGraphQLView
from work_around.settings import DEBUG

urlpatterns = [
    path("", csrf_exempt(jwt_cookie(WorkAroundGraphQLView.as_view(graphiql=True)))),
]

if DEBUG:
    urlpatterns.append(
        path('playground/', GraphQLPlaygroundView.as_view(endpoint="http://localhost:8000/graphql/"))
    )
