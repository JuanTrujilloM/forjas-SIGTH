# external libraries imports
from django.db.models import QuerySet
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, viewsets
from rest_framework.request import Request
from rest_framework.response import Response

# internal application code imports
from employees.filters import EmployeeSnapshotFilterSet
from employees.models import EmployeeSnapshot, MonthlyCut
from employees.serializers import EmployeeSnapshotSerializer
from users.access import EmployeeFieldSearchFilter, EmployeeScopedMixin


# main class
# rows are scoped by the division and section the employee had in that month
class MonthlyCutEmployeeViewSet(
    EmployeeScopedMixin, mixins.ListModelMixin, viewsets.GenericViewSet
):
    queryset = EmployeeSnapshot.objects.all()
    serializer_class = EmployeeSnapshotSerializer
    filter_backends = [DjangoFilterBackend, EmployeeFieldSearchFilter]
    filterset_class = EmployeeSnapshotFilterSet
    search_fields = ['full_name', 'id_number']

    def get_queryset(self) -> QuerySet:
        return super().get_queryset().filter(cut_id=self.kwargs['cut_pk'])

    def list(self, request: Request, *args, **kwargs) -> Response:
        get_object_or_404(MonthlyCut, pk=self.kwargs['cut_pk'])

        return super().list(request, *args, **kwargs)
