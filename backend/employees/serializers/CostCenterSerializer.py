# external libraries imports
from rest_framework import serializers

# internal application code imports
from employees.models import CostCenter


# main class
class CostCenterSerializer(serializers.ModelSerializer):
    class Meta:
        model = CostCenter
        fields = ['id', 'code', 'name', 'is_active']
        read_only_fields = fields
