# external libraries imports
from django.db.models import QuerySet
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
    team_of = django_filters.NumberFilter(field_name='immediate_boss', method='filter_team_of')

    # walked over every employee so an out-of-scope link does not cut the chain, then scoped
    def filter_team_of(self, queryset: QuerySet, name: str, value) -> QuerySet:
        reports: dict[int, list[int]] = {}

        for employee_id, boss_id in Employee.objects.values_list('id', 'immediate_boss_id'):
            reports.setdefault(boss_id, []).append(employee_id)

        team: set[int] = set()
        pending = list(reports.get(int(value), []))

        while pending:
            employee_id = pending.pop()

            if employee_id not in team:
                team.add(employee_id)
                pending.extend(reports.get(employee_id, []))

        return queryset.filter(id__in=team)

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
