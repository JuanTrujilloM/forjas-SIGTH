# external libraries imports
from rest_framework import serializers

# internal application code imports
from employees.models import MonthlyCut


# main class
class MonthlyCutSerializer(serializers.ModelSerializer):
    class Meta:
        model = MonthlyCut
        fields = ['id', 'cut_date', 'updated_at']
        read_only_fields = fields
