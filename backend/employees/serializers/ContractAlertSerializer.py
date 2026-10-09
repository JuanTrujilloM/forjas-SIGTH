# external libraries imports
from django.utils import timezone
from rest_framework import serializers

# internal application code imports
from employees.models import Employee
from employees.services import ContractAlertService
from users.access import EmployeeFieldsMixin


# main class
class ContractAlertSerializer(EmployeeFieldsMixin, serializers.ModelSerializer):
    division_name = serializers.CharField(source='division.name', read_only=True, default=None)
    section_name = serializers.CharField(source='section.name', read_only=True, default=None)
    position_name = serializers.CharField(source='position.name', read_only=True, default=None)
    days_until_contract_end = serializers.SerializerMethodField()
    extension_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Employee
        fields = [
            'id',
            'full_name',
            'id_type',
            'id_number',
            'division_name',
            'section_name',
            'position_name',
            'contract_type',
            'contract_end_date',
            'days_until_contract_end',
            'extension_count',
        ]
        read_only_fields = fields

    def get_days_until_contract_end(self, employee: Employee) -> int:
        return ContractAlertService.days_left(employee.contract_end_date, timezone.localdate())
