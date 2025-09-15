from rest_framework.pagination import LimitOffsetPagination


class CustomPagination(LimitOffsetPagination):
    default_limit=5
    max_limit=10
    # limit_query_param='limit'
    # offset_query_param='offset'