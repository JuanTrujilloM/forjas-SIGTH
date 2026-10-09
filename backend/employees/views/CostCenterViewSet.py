# external libraries imports
from rest_framework import viewsets

# internal application code imports
from employees.models import CostCenter
from employees.serializers import CostCenterSerializer


# main class
class CostCenterViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CostCenter.objects.all()
    serializer_class = CostCenterSerializer
    pagination_class = None
