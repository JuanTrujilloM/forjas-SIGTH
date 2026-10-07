# external libraries imports
from django_filters import rest_framework as django_filters

# internal application code imports
from employees.models import Employee
from users.access import EmployeeFieldFilterSet


# main class
class EmployeeFilterSet(EmployeeFieldFilterSet):
    hire_date_from = django_filters.DateFilter(field_name='hire_date', lookup_expr='gte')
    hire_date_to = django_filters.DateFilter(field_name='hire_date', lookup_expr='lte')
    contract_end_date_from = django_filters.DateFilter(
        field_name='contract_end_date', lookup_expr='gte'
    )
    contract_end_date_to = django_filters.DateFilter(
        field_name='contract_end_date', lookup_expr='lte'
    )
    retirement_date_from = django_filters.DateFilter(
        field_name='retirement_date', lookup_expr='gte'
    )
    retirement_date_to = django_filters.DateFilter(field_name='retirement_date', lookup_expr='lte')

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
