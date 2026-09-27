# external libraries imports
from rest_framework import serializers

# internal application code imports
from employees.models import Position


# main class
class PositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Position
        fields = ['id', 'name', 'is_active']
        read_only_fields = fields
