# external libraries imports
from rest_framework import serializers

# internal application code imports
from employees.models import EmployeeSnapshot
from users.access import EmployeeFieldPolicy


# main class
# the stored columns go through the same matrix as a live employee, trimmed when read
class EmployeeSnapshotSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeSnapshot
        fields = ['employee']
        read_only_fields = fields

    def to_representation(self, snapshot: EmployeeSnapshot) -> dict:
        request = self.context.get('request')
        data = EmployeeFieldPolicy.trim(getattr(request, 'user', None), snapshot.data)

        return {'id': snapshot.employee_id, **data}
