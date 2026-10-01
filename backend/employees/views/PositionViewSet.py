# external libraries imports
from rest_framework import viewsets

# internal application code imports
from employees.models import Position
from employees.serializers import PositionSerializer


# main class
class PositionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Position.objects.all()
    serializer_class = PositionSerializer
    pagination_class = None
