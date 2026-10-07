# internal application code imports
from employees.models import EmployeeSnapshot
from users.access import EmployeeFieldFilterSet


# main class
class EmployeeSnapshotFilterSet(EmployeeFieldFilterSet):
    class Meta:
        model = EmployeeSnapshot
        fields = ['status', 'division', 'section']
