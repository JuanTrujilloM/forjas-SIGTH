# external libraries imports
from rest_framework import serializers

# internal application code imports
from employees.models import Employee
from users.access import EmployeeFieldsMixin

from .EmployeePhotoUrlField import EmployeePhotoUrlField


# main class
class EmployeeListSerializer(EmployeeFieldsMixin, serializers.ModelSerializer):
    photo_thumbnail = EmployeePhotoUrlField(thumbnail=True)
    division_name = serializers.CharField(source='division.name', read_only=True, default=None)
    section_name = serializers.CharField(source='section.name', read_only=True, default=None)
    position_name = serializers.CharField(source='position.name', read_only=True, default=None)

    class Meta:
        model = Employee
        fields = [
            'id',
            'status',
            'id_type',
            'id_number',
            'full_name',
            'photo_thumbnail',
            'division_name',
            'section_name',
            'position_name',
        ]
        read_only_fields = fields
