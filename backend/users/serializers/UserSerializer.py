# external libraries imports
from rest_framework import serializers

# internal application code imports
from users.access import DivisionScopePolicy
from users.models import User


# main class
class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    division_name = serializers.CharField(source='division.name', read_only=True, default=None)
    sees_every_division = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'first_name',
            'last_name',
            'full_name',
            'division',
            'division_name',
            'sees_every_division',
        ]
        read_only_fields = fields

    def get_full_name(self, user: User) -> str:
        return user.get_full_name() or user.email
    
    def get_sees_every_division(self, user: User) -> bool:
        return DivisionScopePolicy.sees_every_division(user)
