# external libraries imports
from rest_framework import serializers

# internal application code imports
from users.models import Section


# main class
class SectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Section
        fields = ['id', 'name', 'is_active']
        read_only_fields = fields
