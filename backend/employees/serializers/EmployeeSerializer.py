# external libraries imports
from rest_framework import serializers

# internal application code imports
from employees.enums import EmployeeStatus
from employees.models import Employee
from users.access import EmployeeFieldsMixin

from .ContractExtensionSerializer import ContractExtensionSerializer
from .EmployeePhotoUrlField import EmployeePhotoUrlField


# main code
REQUIRED_MESSAGE = 'Este campo es obligatorio.'


# main class
class EmployeeSerializer(EmployeeFieldsMixin, serializers.ModelSerializer):
    photo = EmployeePhotoUrlField()
    age = serializers.IntegerField(read_only=True)
    seniority = serializers.ReadOnlyField()
    hourly_rate = serializers.DecimalField(max_digits=14, decimal_places=2, read_only=True)
    division_name = serializers.CharField(source='division.name', read_only=True, default=None)
    section_name = serializers.CharField(source='section.name', read_only=True, default=None)
    position_name = serializers.CharField(source='position.name', read_only=True, default=None)
    cost_center_code = serializers.CharField(
        source='cost_center.code', read_only=True, default=None
    )
    cost_center_name = serializers.CharField(
        source='cost_center.name', read_only=True, default=None
    )
    previous_position_name = serializers.CharField(
        source='previous_position.name', read_only=True, default=None
    )
    immediate_boss_name = serializers.CharField(
        source='immediate_boss.full_name', read_only=True, default=None
    )
    extensions = ContractExtensionSerializer(many=True, read_only=True)

    class Meta:
        model = Employee
        fields = [
            'id',
            'status',
            'id_type',
            'id_number',
            'full_name',
            'photo',
            'birth_date',
            'age',
            'sex',
            'blood_type',
            'marital_status',
            'has_children',
            'mobile_phone',
            'personal_email',
            'address',
            'neighborhood',
            'city',
            'education_level',
            'degree_title',
            'employment_type',
            'category',
            'division',
            'division_name',
            'evaluation_group',
            'collective_agreement',
            'position',
            'position_name',
            'position_start_date',
            'previous_position',
            'previous_position_name',
            'previous_position_start_date',
            'previous_position_end_date',
            'is_leader',
            'section',
            'section_name',
            'cost_center',
            'cost_center_code',
            'cost_center_name',
            'area',
            'additional_role',
            'immediate_boss',
            'immediate_boss_name',
            'hire_date',
            'retirement_date',
            'seniority',
            'training',
            'current_salary',
            'salary_type',
            'hourly_rate',
            'transport_allowance',
            'contract_type',
            'contract_end_date',
            'extensions',
            'indefinite_extension',
            'occupational_risk_insurer',
            'health_insurer',
            'pension_fund',
            'severance_fund',
            'notes',
            'birth_municipality',
            'nationality',
            'ethnicity',
            'family_composition',
            'dependents_count',
            'socioeconomic_stratum',
        ]

    def get_fields(self) -> dict:
        fields = super().get_fields()

        for field in fields.values():
            if field.required:
                field.error_messages.update(
                    required=REQUIRED_MESSAGE, null=REQUIRED_MESSAGE, blank=REQUIRED_MESSAGE
                )

        return fields

    def validate(self, attrs: dict) -> dict:
        attrs = super().validate(attrs)
        boss = attrs.get('immediate_boss')

        if boss is not None and self.instance is not None and boss.pk == self.instance.pk:
            raise serializers.ValidationError(
                {'immediate_boss': 'Un empleado no puede ser su propio jefe inmediato.'}
            )

        start = self._merged(attrs, 'previous_position_start_date')
        end = self._merged(attrs, 'previous_position_end_date')

        if start and end and end < start:
            raise serializers.ValidationError({
                'previous_position_end_date':
                    'La fecha de fin del cargo anterior no puede ser anterior a la de inicio.',
            })

        status = self._merged(attrs, 'status')

        if status == EmployeeStatus.ACTIVE:
            attrs['retirement_date'] = None

        errors = Employee.retirement_errors(
            status, self._merged(attrs, 'retirement_date'), self._merged(attrs, 'hire_date')
        )

        if errors:
            raise serializers.ValidationError(errors)

        return attrs

    def _merged(self, attrs: dict, name: str):
        if name in attrs:
            return attrs[name]

        return getattr(self.instance, name, None)
