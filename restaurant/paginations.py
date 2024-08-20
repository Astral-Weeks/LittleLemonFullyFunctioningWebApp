from rest_framework import pagination

class MenuItemPagination(pagination.PageNumberPagination):
    page_size = 4
    page_size_query_param = 'perpage'
    max_page_size = 20
    page_query_param = 'page'