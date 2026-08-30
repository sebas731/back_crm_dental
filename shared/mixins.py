class QueryParamFilterMixin:
    """
    Filtra el queryset por parámetros de query exactos.

    Declarar ``filterset_params`` con los nombres de campos permitidos:

        class MyViewSet(QueryParamFilterMixin, viewsets.ModelViewSet):
            filterset_params = ["paciente", "estado"]
    """

    filterset_params: list[str] = []

    def get_queryset(self):
        queryset = super().get_queryset()
        filters = {
            param: self.request.query_params[param]
            for param in self.filterset_params
            if self.request.query_params.get(param)
        }
        return queryset.filter(**filters) if filters else queryset
