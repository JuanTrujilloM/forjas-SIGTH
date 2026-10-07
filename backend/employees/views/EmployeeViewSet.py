# external libraries imports
from django.http import Http404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

# internal application code imports
from employees.filters import EmployeeFilterSet
from employees.models import Employee
from employees.serializers import (
    ContractExtensionRequestSerializer,
    ContractExtensionSerializer,
    EmployeeListSerializer,
    EmployeePhotoSerializer,
    EmployeeSerializer,
)
from employees.services import ContractExtensionService, EmployeePhotoService
from users.access import (
    EmployeeFieldOrderingFilter,
    EmployeeFieldPolicy,
    EmployeeFieldSearchFilter,
    EmployeeScopedMixin,
    EmployeeWritePermission,
)


# main class
# no destroy: an employee is retired by changing their status, never deleted
class EmployeeViewSet(
    EmployeeScopedMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Employee.objects.select_related(
        'division', 'section', 'position', 'previous_position', 'immediate_boss', 'cost_center'
    ).prefetch_related('extensions')
    permission_classes = [IsAuthenticated, EmployeeWritePermission]
    filter_backends = [DjangoFilterBackend, EmployeeFieldSearchFilter, EmployeeFieldOrderingFilter]
    filterset_class = EmployeeFilterSet
    search_fields = ['full_name', 'id_number']
    ordering_fields = ['full_name', 'id_number', 'hire_date', 'birth_date', 'contract_end_date']
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

    # GET only serves the form that registers one, so it is as restricted as the POST
    @action(detail=True, methods=['get', 'post'], serializer_class=ContractExtensionRequestSerializer)
    def extensions(self, request: Request, pk: str | None = None) -> Response:
        employee = self.get_object()

        if not EmployeeFieldPolicy.can_write(request.user):
            raise PermissionDenied('Solo Talento Humano puede registrar prórrogas.')

        if request.method == 'GET':
            return Response({
                'suggested_end_date': ContractExtensionService.suggest_end_date(employee),
            })

        serializer = ContractExtensionRequestSerializer(
            data=request.data, context={'employee': employee}
        )
        serializer.is_valid(raise_exception=True)
        extension = ContractExtensionService.register(
            employee, serializer.validated_data['new_contract_end_date']
        )

        return Response(
            {
                **ContractExtensionSerializer(extension).data,
                'contract_end_date': employee.contract_end_date,
            },
            status=status.HTTP_201_CREATED,
        )

    @action(
        detail=True,
        methods=['get', 'put', 'delete'],
        parser_classes=[MultiPartParser],
        serializer_class=EmployeePhotoSerializer,
    )
    def photo(self, request: Request, pk: str | None = None):
        employee = self.get_object()

        if 'photo' not in EmployeeFieldPolicy.readable_fields(request.user):
            raise Http404

        if request.method == 'GET':
            name = employee.photo.name if employee.photo else ''

            if request.query_params.get('size') == 'thumb':
                return EmployeePhotoService.thumbnail_response(name)

            return EmployeePhotoService.response(name)

        if request.method == 'DELETE':
            EmployeePhotoService.remove(employee)
            return Response(status=status.HTTP_204_NO_CONTENT)

        serializer = EmployeePhotoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        EmployeePhotoService.replace(employee, serializer.validated_data['photo'])

        return Response(
            {'photo': EmployeeSerializer(employee, context={'request': request}).data['photo']}
        )
