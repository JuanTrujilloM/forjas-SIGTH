# external libraries imports
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

# internal application code imports
from employees.filters import EmployeeFilterSet
from employees.models import Employee
from employees.serializers import (
    ContractExtensionSerializer,
    EmployeeListSerializer,
    EmployeeSerializer,
)
from users.access import (
    EmployeeFieldOrderingFilter,
    EmployeeFieldPolicy,
    EmployeeFieldSearchFilter,
    EmployeeScopedMixin,
    EmployeeWritePermission,
)


# main class
# No destroy: an employee is retired by changing their status, never deleted (6.3)
class EmployeeViewSet(
    EmployeeScopedMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Employee.objects.select_related(
        'division', 'section', 'position', 'previous_position', 'immediate_boss'
    ).prefetch_related('extensions')
    permission_classes = [IsAuthenticated, EmployeeWritePermission]
    filter_backends = [DjangoFilterBackend, EmployeeFieldSearchFilter, EmployeeFieldOrderingFilter]
    filterset_class = EmployeeFilterSet
    search_fields = ['full_name', 'id_number']
    ordering_fields = ['full_name', 'id_number', 'hire_date', 'birth_date']
    ordering = ['full_name', 'id']

    def get_serializer_class(self):
        if self.action == 'list':
            return EmployeeListSerializer

        return EmployeeSerializer

    @action(detail=False, methods=['get'], pagination_class=None)
    def choices(self, request: Request) -> Response:
        readable = EmployeeFieldPolicy.readable_fields(request.user)

        return Response({
            field.name: [{'value': value, 'label': label} for value, label in field.choices]
            for field in Employee._meta.concrete_fields
            if field.choices and field.name in readable
        })

    @action(detail=True, methods=['post'], serializer_class=ContractExtensionSerializer)
    def extensions(self, request: Request, pk: str | None = None) -> Response:
        serializer = ContractExtensionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(employee=self.get_object())

        return Response(serializer.data, status=status.HTTP_201_CREATED)
