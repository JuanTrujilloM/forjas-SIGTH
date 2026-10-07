# external libraries imports
from rest_framework import serializers

# internal application code imports
from users.access import EmployeeFieldPolicy, EmployeeScopePolicy
from users.models import User


# main class
class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    profile_name = serializers.CharField(source='get_profile_display', read_only=True)
    division_name = serializers.CharField(source='division.name', read_only=True, default=None)
    section_names = serializers.SerializerMethodField()
    sees_every_employee = serializers.SerializerMethodField()
    can_edit_employees = serializers.SerializerMethodField()
    readable_fields = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'first_name',
            'last_name',
            'full_name',
            'profile',
            'profile_name',
            'division',
            'division_name',
            'section_names',
            'sees_every_employee',
            'can_edit_employees',
            'readable_fields',
        ]
        read_only_fields = fields

    def get_full_name(self, user: User) -> str:
        return user.get_full_name() or user.email

    def get_section_names(self, user: User) -> list[str]:
        return [section.name for section in user.sections.all()]

    def get_sees_every_employee(self, user: User) -> bool:
        return EmployeeScopePolicy.sees_every_employee(user)

    def get_can_edit_employees(self, user: User) -> bool:
        return EmployeeFieldPolicy.can_write(user)

    def get_readable_fields(self, user: User) -> list[str]:
        return sorted(EmployeeFieldPolicy.readable_fields(user))
