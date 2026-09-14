from rest_framework.pagination import PageNumberPagination


class StandardPagination(PageNumberPagination):
    """Paginación por defecto de todos los list del sistema.

    - 15 elementos por página (lo que espera el front).
    - El cliente puede pedir otro tamaño con ?page_size=N, pero nunca más de 15.
    """

    page_size = 15
    page_size_query_param = "page_size"
    max_page_size = 15
