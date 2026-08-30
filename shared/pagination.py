from rest_framework.pagination import PageNumberPagination


class StandardPagination(PageNumberPagination):
    """Paginación por defecto que permite al cliente pedir un tamaño mayor
    con ?page_size=N (hasta max_page_size), útil para catálogos completos."""

    page_size_query_param = "page_size"
    max_page_size = 500
