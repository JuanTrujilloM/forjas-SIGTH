# external libraries imports
from rest_framework import serializers

# internal application code imports
from users.models import Division


# main class
class DivisionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Division
        fields = ['id', 'name', 'is_active']
        read_only_fields = fields
