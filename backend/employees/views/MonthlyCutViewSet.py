# external libraries imports
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.request import Request
from rest_framework.response import Response

# internal application code imports
from employees.models import MonthlyCut
from employees.serializers import MonthlyCutSerializer
from employees.services import MonthlyCutService
from users.access import EmployeeFieldPolicy


# main class
class MonthlyCutViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = MonthlyCut.objects.all()
    serializer_class = MonthlyCutSerializer
    pagination_class = None

    @action(detail=True, methods=['post'])
    def retake(self, request: Request, pk: str | None = None) -> Response:
        if not EmployeeFieldPolicy.can_write(request.user):
            raise PermissionDenied('Solo Talento Humano puede rehacer un corte.')

        cut = self.get_object()

        if MonthlyCut.objects.filter(cut_date__gt=cut.cut_date).exists():
            raise ValidationError({'detail': ['Solo se puede rehacer el último corte.']})

        MonthlyCutService.retake(cut, request.user)

        return Response(self.get_serializer(cut).data)
