# external libraries imports
from rest_framework import viewsets

# internal application code imports
from users.models import Division
from users.serializers import DivisionSerializer


# main class
class DivisionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Division.objects.all()
    serializer_class = DivisionSerializer
    pagination_class = None
