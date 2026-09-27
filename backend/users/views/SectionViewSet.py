# external libraries imports
from rest_framework import viewsets

# internal application code imports
from users.models import Section
from users.serializers import SectionSerializer


# main class
class SectionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Section.objects.all()
    serializer_class = SectionSerializer
    pagination_class = None
