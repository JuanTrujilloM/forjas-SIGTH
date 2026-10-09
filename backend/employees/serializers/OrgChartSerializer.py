# external libraries imports
from rest_framework import serializers

# internal application code imports
from employees.models import Employee
from users.access import EmployeeFieldsMixin

from .EmployeePhotoUrlField import EmployeePhotoUrlField


# main class
class OrgChartSerializer(EmployeeFieldsMixin, serializers.ModelSerializer):
    photo_thumbnail = EmployeePhotoUrlField(thumbnail=True)
    division_name = serializers.CharField(source='division.name', read_only=True, default=None)
    section_name = serializers.CharField(source='section.name', read_only=True, default=None)
    position_name = serializers.CharField(source='position.name', read_only=True, default=None)
    immediate_boss_name = serializers.CharField(
        source='immediate_boss.full_name', read_only=True, default=None
    )

    class Meta:
        model = Employee
        fields = [
            'id',
            'full_name',
            'photo_thumbnail',
            'division',
            'division_name',
            'section',
            'section_name',
            'position_name',
            'immediate_boss',
            'immediate_boss_name',
        ]
        read_only_fields = fields
