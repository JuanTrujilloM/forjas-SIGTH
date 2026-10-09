# external libraries imports
from datetime import date

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

# internal application code imports
from employees.models import MonthlyCut
from employees.services import MonthlyCutService


# main class
class Command(BaseCommand):
    help = (
        'Toma el corte mensual de los empleados. Va en la misma tarea diaria que el aviso de '
        'vencimientos: el día 1 toma el corte del mes que terminó; los demás días no hace nada.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--date',
            type=date.fromisoformat,
            help='Toma el corte de esta fecha (AAAA-MM-DD, último día de un mes) en vez del '
                 'mes que acaba de terminar.',
        )

    def handle(self, *args, **options):
        today = timezone.localdate()
        cut_date = options['date']

        if cut_date is None:
            if today.day != 1:
                self.stdout.write('Hoy no es día de corte: el corte se toma el día 1.')
                return

            cut_date = MonthlyCutService.previous_month_end(today)

        if not MonthlyCutService.is_month_end(cut_date):
            raise CommandError('La fecha de corte tiene que ser el último día de un mes.')

        if cut_date > today:
            raise CommandError('No se puede tomar el corte de un mes que no ha terminado.')

        if MonthlyCut.objects.filter(cut_date=cut_date).exists():
            self.stdout.write(f'El corte al {cut_date:%d/%m/%Y} ya existe; no se repite.')
            return

        cut = MonthlyCutService.take(cut_date)
        self.stdout.write(self.style.SUCCESS(
            f'Corte al {cut_date:%d/%m/%Y} tomado con {cut.snapshots.count()} empleados.'
        ))
