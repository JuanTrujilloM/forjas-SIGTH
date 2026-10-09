# external libraries imports
from django.db.models import Count
from django.http import Http404, HttpResponse
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

# internal application code imports
from employees.enums import EmployeeStatus
from employees.filters import EmployeeFilterSet
from employees.models import Employee
from employees.serializers import (
    ContractAlertSerializer,
    ContractExtensionRequestSerializer,
    ContractExtensionSerializer,
    EmployeeListSerializer,
    EmployeePhotoSerializer,
    EmployeeSerializer,
    OrgChartSerializer,
)
from employees.services import (
    ContractAlertService,
    ContractExtensionService,
    EmployeeExportService,
    EmployeePhotoService,
)
from users.access import (
    ContractAlertPermission,
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

    @action(
        detail=False,
        methods=['get'],
        url_path='contract-alerts',
        pagination_class=None,
        permission_classes=[IsAuthenticated, ContractAlertPermission],
    )
    def contract_alerts(self, request: Request) -> Response:
        employees = ContractAlertService.pending(
            self.get_queryset(), timezone.localdate()
        ).annotate(extension_count=Count('extensions'))

        serializer = ContractAlertSerializer(
            employees, many=True, context=self.get_serializer_context()
        )

        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='export-fields', pagination_class=None)
    def export_fields(self, request: Request) -> Response:
        readable = EmployeeFieldPolicy.readable_fields(request.user)

        return Response(EmployeeExportService.available_columns(readable))

    @action(detail=False, methods=['get'])
    def report(self, request: Request) -> Response:
        columns = self._export_columns(request)
        employees = self.paginate_queryset(
            EmployeeExportService.prepare(self.filter_queryset(self.get_queryset()))
        )
        rows = EmployeeExportService.rows(employees, columns)
        response = self.get_paginated_response([
            {
                'id': employee.id,
                'values': [
                    EmployeeExportService.display(value, column.kind)
                    for value, column in zip(row, columns)
                ],
            }
            for employee, row in zip(employees, rows)
        ])
        response.data['columns'] = [{'key': column.key, 'label': column.label} for column in columns]

        return response

    @action(detail=False, methods=['get'])
    def export(self, request: Request) -> HttpResponse:
        file_format = request.query_params.get('file_format', '')

        if file_format not in EmployeeExportService.FORMATS:
            raise ValidationError({'file_format': ['Elige Excel, CSV o PDF.']})

        columns = self._export_columns(request)
        rows = EmployeeExportService.rows(
            EmployeeExportService.prepare(self.filter_queryset(self.get_queryset())), columns
        )
        title = request.query_params.get('title', '').strip()[:200] or 'Reporte de empleados'
        description = request.query_params.get('description', '').strip()[:500]

        content = EmployeeExportService.render(file_format, title, description, columns, rows)

        response = HttpResponse(content, content_type=EmployeeExportService.FORMATS[file_format])
        response['Content-Disposition'] = (
            f'attachment; filename="{EmployeeExportService.file_name(file_format)}"'
        )

        return response

    def _export_columns(self, request: Request) -> list:
        requested = [key.strip() for key in request.query_params.get('fields', '').split(',')]
        columns = EmployeeExportService.columns_for(
            EmployeeFieldPolicy.readable_fields(request.user), requested
        )

        if not columns:
            raise ValidationError({'fields': ['Elige al menos un campo para el reporte.']})

        return columns

    @action(detail=False, methods=['get'], url_path='org-chart', pagination_class=None)
    def org_chart(self, request: Request) -> Response:
        employees = self.get_queryset().filter(status=EmployeeStatus.ACTIVE).order_by('full_name')
        serializer = OrgChartSerializer(
            employees, many=True, context=self.get_serializer_context()
        )

        return Response(serializer.data)

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
