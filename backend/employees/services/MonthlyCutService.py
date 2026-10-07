# external libraries imports
import calendar
from datetime import date, timedelta
from typing import TYPE_CHECKING

from django.db import transaction
from django.db.models import Q

# internal application code imports
from employees.enums import EmployeeStatus

from .EmployeeRowService import EmployeeRowService

# type hints only: importing the models at runtime would be circular
if TYPE_CHECKING:
    from employees.models import MonthlyCut


# main code
# imported on use: employees.models imports this package, so a top-level import is circular
def _models():
    from employees import models

    return models


# main class
class MonthlyCutService:
    @staticmethod
    def month_end(day: date) -> date:
        return day.replace(day=calendar.monthrange(day.year, day.month)[1])

    @staticmethod
    def previous_month_end(day: date) -> date:
        return day.replace(day=1) - timedelta(days=1)

    @staticmethod
    def is_month_end(day: date) -> bool:
        return day == MonthlyCutService.month_end(day)

    @staticmethod
    @transaction.atomic
    def take(cut_date: date, user=None) -> 'MonthlyCut':
        cut = _models().MonthlyCut.objects.create(cut_date=cut_date, taken_by=user)
        MonthlyCutService._store_snapshots(cut)

        return cut

    # only the latest cut is retaken, right after closing: older months stay as they were
    @staticmethod
    @transaction.atomic
    def retake(cut: 'MonthlyCut', user) -> 'MonthlyCut':
        cut.snapshots.all().delete()
        cut.taken_by = user
        cut.save(update_fields=['taken_by', 'updated_at'])
        MonthlyCutService._store_snapshots(cut)

        return cut

    # who belongs to a month: active then, plus whoever retired during that month
    @staticmethod
    def _store_snapshots(cut: 'MonthlyCut') -> None:
        models = _models()
        month_start = cut.cut_date.replace(day=1)
        employees = EmployeeRowService.prepare(
            models.Employee.objects.filter(hire_date__lte=cut.cut_date).filter(
                Q(status=EmployeeStatus.ACTIVE)
                | Q(retirement_date__gte=month_start, retirement_date__lte=cut.cut_date)
            )
        )

        models.EmployeeSnapshot.objects.bulk_create([
            models.EmployeeSnapshot(
                cut=cut,
                employee=employee,
                full_name=employee.full_name,
                id_number=employee.id_number,
                status=employee.status,
                division_id=employee.division_id,
                section_id=employee.section_id,
                data=EmployeeRowService.row(employee, cut.cut_date),
            )
            for employee in employees
        ])
