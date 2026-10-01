# external libraries imports
from rest_framework import serializers

# internal application code imports
from employees.models import ContractExtension


# main class
class ContractExtensionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContractExtension
        fields = ['id', 'extension_date']
