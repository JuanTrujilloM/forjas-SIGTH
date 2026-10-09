# external libraries imports
from datetime import date
from decimal import ROUND_HALF_UP, Decimal
from typing import TYPE_CHECKING

# type hints only: importing the models at runtime would be circular
if TYPE_CHECKING:
    from employees.models import Employee


# main code
RELATED_NAMES = {
    'division_name': ('division', 'name'),
    'section_name': ('section', 'name'),
    'position_name': ('position', 'name'),
    'previous_position_name': ('previous_position', 'name'),
    'cost_center_code': ('cost_center', 'code'),
    'cost_center_name': ('cost_center', 'name'),
    'immediate_boss_name': ('immediate_boss', 'full_name'),
}

SKIPPED_FIELDS = {'id', 'photo', 'created_at', 'updated_at'}


# main class
class EmployeeRowService:
    @staticmethod
    def prepare(queryset):
        return queryset.select_related(
            'division', 'section', 'position', 'previous_position', 'immediate_boss', 'cost_center'
        ).prefetch_related('extensions')

    @staticmethod
    def row(employee: 'Employee', on: date) -> dict:
        row = {}

        for field in employee._meta.concrete_fields:
            if field.name in SKIPPED_FIELDS:
                continue

            row[field.name] = EmployeeRowService._plain(getattr(employee, field.attname))

        for key, (relation, attribute) in RELATED_NAMES.items():
            related = getattr(employee, relation)
            row[key] = getattr(related, attribute) if related is not None else None

        months_old = employee.whole_months_between(employee.birth_date, on)
        months_hired = employee.whole_months_between(employee.hire_date, on)
        row['age'] = months_old // 12
        row['seniority'] = {'years': months_hired // 12, 'months': months_hired % 12}
        row['hourly_rate'] = EmployeeRowService._plain(
            (employee.current_salary / employee.MONTHLY_WORK_HOURS).quantize(
                Decimal('0.01'), rounding=ROUND_HALF_UP
            )
        )
        row['extensions'] = [
            {'id': extension.id, 'extension_date': extension.extension_date.isoformat()}
            for extension in employee.extensions.all()
            if extension.extension_date <= on
        ]

        return row

    @staticmethod
    def _plain(value):
        if isinstance(value, date):
            return value.isoformat()

        if isinstance(value, Decimal):
            return str(value)

        return value
