# external libraries imports
from rest_framework import serializers

# internal application code imports
from employees.services import ContractExtensionService


# main class
class ContractExtensionRequestSerializer(serializers.Serializer):
    new_contract_end_date = serializers.DateField(
        error_messages={'required': 'Este campo es obligatorio.', 'null': 'Este campo es obligatorio.'}
    )

    def validate(self, attrs: dict) -> dict:
        employee = self.context['employee']
        current_end = employee.contract_end_date

        if current_end is None:
            raise serializers.ValidationError({
                'detail': 'El empleado no tiene fecha de vencimiento; regístrala en su ficha antes '
                          'de agregar una prórroga.',
            })

        if attrs['new_contract_end_date'] <= current_end:
            raise serializers.ValidationError({
                'new_contract_end_date': 'La nueva fecha de vencimiento debe ser posterior a la '
                                         f'actual ({current_end:%d/%m/%Y}).',
            })

        start = ContractExtensionService.start_date(employee)

        if employee.extensions.filter(extension_date=start).exists():
            raise serializers.ValidationError({
                'detail': f'Ya hay una prórroga que rige desde el {start:%d/%m/%Y}.',
            })

        return attrs
