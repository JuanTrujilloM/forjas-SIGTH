# internal application code imports
from employees.models import Employee
from users.access import EmployeeFieldFilterSet


# main class
class EmployeeFilterSet(EmployeeFieldFilterSet):
    class Meta:
        model = Employee
        fields = [
            'status',
            'division',
            'section',
            'position',
            'category',
            'employment_type',
            'evaluation_group',
            'contract_type',
            'cost_center',
            'area',
            'sex',
            'is_leader',
        ]
