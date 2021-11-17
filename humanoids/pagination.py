from rest_framework.pagination import PageNumberPagination

class HumanoidsPaginator(PageNumberPagination):
    page_size = 4
    page_query_param = 'pag'