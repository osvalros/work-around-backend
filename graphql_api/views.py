import logging

from graphene_django.views import GraphQLView

logger = logging.getLogger(__name__)

DEFAULT_CONTEXT_VARIABLES = {}


def set_default_request_context_variables(request):
    for k, v in DEFAULT_CONTEXT_VARIABLES.items():
        setattr(request, k, v)


class WorkAroundGraphQLView(GraphQLView):
    def execute_graphql_request(self, request, *args, **kwargs):
        set_default_request_context_variables(request)
        result = super().execute_graphql_request(request, *args, **kwargs)
        if result.errors:
            for error in result.errors:
                try:
                    raise error.original_error
                except Exception as e:
                    logger.exception(e)
        return result
