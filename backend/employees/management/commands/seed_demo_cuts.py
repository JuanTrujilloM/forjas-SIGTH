# external libraries imports
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

# internal application code imports
from employees.enums import EmployeeStatus
from employees.models import Employee, EmployeeSnapshot, MonthlyCut
from employees.services import EmployeeRowService, MonthlyCutService


# main class
class Command(BaseCommand):
    help = (
        'Solo para desarrollo: arma cortes mensuales aproximados de los últimos meses con las '
        'fechas de ingreso y retiro, para probar la evolución y las comparaciones de la '
        'analítica. Los cortes reales los toma take_monthly_cut.'
    )

    def add_arguments(self, parser):
        parser.add_argument('--months', type=int, default=12, help='Meses hacia atrás (12).')
        parser.add_argument(
            '--replace', action='store_true', help='Borra todos los cortes antes de armarlos.'
        )

    def handle(self, *args, **options):
        if not settings.DEBUG:
            raise CommandError('Los cortes de demostración solo se arman con DEBUG=True.')

        if MonthlyCut.objects.exists() and not options['replace']:
            raise CommandError('Ya hay cortes. Usa --replace para borrarlos y armarlos de nuevo.')

        cut_date = MonthlyCutService.previous_month_end(timezone.localdate())
        cut_dates = []

        for _ in range(options['months']):
            cut_dates.append(cut_date)
            cut_date = MonthlyCutService.previous_month_end(cut_date)

        employees = list(EmployeeRowService.prepare(Employee.objects.all()))

        with transaction.atomic():
            if options['replace']:
                EmployeeSnapshot.objects.all().delete()
                MonthlyCut.objects.all().delete()

            for cut_date in sorted(cut_dates):
                cut = MonthlyCut.objects.create(cut_date=cut_date)
                EmployeeSnapshot.objects.bulk_create(
                    snapshot
                    for employee in employees
                    if (snapshot := self._snapshot(cut, employee)) is not None
                )

        self.stdout.write(self.style.SUCCESS(
            f'{len(cut_dates)} cortes de demostración armados, del '
            f'{min(cut_dates):%d/%m/%Y} al {max(cut_dates):%d/%m/%Y}.'
        ))

    # approximate on purpose: today's section and salary stand in for the ones of that month
    def _snapshot(self, cut: MonthlyCut, employee: Employee) -> EmployeeSnapshot | None:
        month_start = cut.cut_date.replace(day=1)
        retired_on = employee.retirement_date

        if employee.hire_date > cut.cut_date or (retired_on and retired_on < month_start):
            return None

        retired = retired_on is not None and retired_on <= cut.cut_date
        status = EmployeeStatus.RETIRED if retired else EmployeeStatus.ACTIVE
        data = EmployeeRowService.row(employee, cut.cut_date)
        data['status'] = status
        data['retirement_date'] = retired_on.isoformat() if retired else None

        return EmployeeSnapshot(
            cut=cut,
            employee=employee,
            full_name=employee.full_name,
            id_number=employee.id_number,
            status=status,
            division_id=employee.division_id,
            section_id=employee.section_id,
            data=data,
        )
