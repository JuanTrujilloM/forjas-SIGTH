# external libraries imports
from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError


# main class
class Command(BaseCommand):
    help = (
        'Solo para desarrollo: deja la base lista para probar todo el SIGTH. Recrea los '
        'empleados, las cuentas y los cortes mensuales de demostración, en ese orden. Lo que '
        'se puede probar con cada cuenta está en docs/guias/demo-funcionalidades.md.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--seed', type=int, default=2026, help='Semilla de los datos aleatorios (2026).'
        )

    def handle(self, *args, **options):
        if not settings.DEBUG:
            raise CommandError('La demostración solo se arma con DEBUG=True.')

        self.stdout.write(self.style.MIGRATE_HEADING('Empleados'))
        call_command('seed_demo_employees', replace=True, seed=options['seed'], stdout=self.stdout)

        self.stdout.write(self.style.MIGRATE_HEADING('Cuentas'))
        call_command('seed_demo_users', replace=True, stdout=self.stdout)

        self.stdout.write(self.style.MIGRATE_HEADING('Cortes mensuales'))
        call_command('seed_demo_cuts', replace=True, stdout=self.stdout)

        self.stdout.write(self.style.SUCCESS(
            'Demostración lista. Entra con demo.<perfil>@<dominio> y la contraseña de '
            'DEMO_USERS_PASSWORD.'
        ))
