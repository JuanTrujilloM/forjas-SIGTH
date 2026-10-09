# external libraries imports
import calendar
from datetime import date, timedelta
from typing import TYPE_CHECKING

from django.db import transaction

# internal application code imports
from employees.enums import ContractType

# type hints only: importing the models at runtime would be circular
if TYPE_CHECKING:
    from employees.models import ContractExtension, Employee


# main class
class ContractExtensionService:
    TERM_MONTHS = {
        ContractType.FIXED_THREE_MONTHS: 3,
        ContractType.FIXED_SIX_MONTHS: 6,
        ContractType.FIXED_ONE_YEAR: 12,
    }
    # a fixed term under a year renews for the same term three times, then for at least a year
    SAME_TERM_RENEWALS = 3

    @staticmethod
    def suggest_end_date(employee: 'Employee') -> date | None:
        months = ContractExtensionService.TERM_MONTHS.get(employee.contract_type)

        if months is None or employee.contract_end_date is None:
            return None

        if months < 12 and employee.extensions.count() >= ContractExtensionService.SAME_TERM_RENEWALS:
            months = 12

        start = ContractExtensionService.start_date(employee)

        return ContractExtensionService._add_months(start, months) - timedelta(days=1)

    @staticmethod
    def start_date(employee: 'Employee') -> date:
        return employee.contract_end_date + timedelta(days=1)

    @staticmethod
    @transaction.atomic
    def register(employee: 'Employee', new_end_date: date) -> 'ContractExtension':
        extension = employee.extensions.create(
            extension_date=ContractExtensionService.start_date(employee)
        )
        employee.contract_end_date = new_end_date
        employee.save(update_fields=['contract_end_date', 'updated_at'])

        return extension

    @staticmethod
    def _add_months(start: date, months: int) -> date:
        month_index = start.month - 1 + months
        year = start.year + month_index // 12
        month = month_index % 12 + 1
        day = min(start.day, calendar.monthrange(year, month)[1])

        return date(year, month, day)
