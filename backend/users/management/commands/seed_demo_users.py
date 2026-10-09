# external libraries imports
from decouple import config
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

# internal application code imports
from employees.models import MonthlyCut
from users.enums import AccessProfile
from users.models import Division, Section, User, UserSection

# main code
DEMO_PREFIX = 'demo.'
MIN_PASSWORD_LENGTH = 12

# local part of the email, last name, profile, division, sections, is_staff
DEMO_USERS = [
    ('talento', 'Talento Humano', AccessProfile.TALENT_MANAGEMENT, None, [], True),
    ('gerencia', 'Gerencia General', AccessProfile.GENERAL_MANAGEMENT, None, [], False),
    ('sst', 'SST - SGI', AccessProfile.OCCUPATIONAL_SAFETY, None, [], False),
    ('director', 'Director Procesos Técnicos', AccessProfile.DIRECTOR,
     'Dir. Procesos Técnicos', [], False),
    ('lider', 'Líder Calidad y Mantenimiento', AccessProfile.LEADER, None,
     ['Calidad', 'Mantenimiento'], False),
    ('coordinador', 'Coordinador Soldadura', AccessProfile.LEADER, None, ['Soldadura'], False),
    ('ti', 'TI', '', None, [], True),
]


class Command(BaseCommand):
    help = (
        'Crea una cuenta de demostración por perfil de acceso. Solo en desarrollo '
        '(DEBUG=True); la contraseña sale de DEMO_USERS_PASSWORD en el .env.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--replace',
            action='store_true',
            help='Borra antes las cuentas de demostración que ya existan.',
        )

    def handle(self, *args, **options):
        if not settings.DEBUG:
            raise CommandError('Las cuentas de demostración solo se crean con DEBUG=True.')

        # read from .env and never taken as an argument: it would stay in the shell history
        password = config('DEMO_USERS_PASSWORD', default='')

        if len(password) < MIN_PASSWORD_LENGTH:
            raise CommandError(
                f'Define DEMO_USERS_PASSWORD en backend/.env, de al menos '
                f'{MIN_PASSWORD_LENGTH} caracteres.'
            )

        domain = settings.CORPORATE_EMAIL_DOMAIN
        existing = User.objects.filter(email__startswith=DEMO_PREFIX, email__endswith=f'@{domain}')

        if existing.exists() and not options['replace']:
            raise CommandError(
                f'Ya hay {existing.count()} cuentas de demostración. Usa --replace para recrearlas.'
            )

        with transaction.atomic():
            if options['replace']:
                self._remove(existing)

            for local_part, last_name, profile, division, sections, is_staff in DEMO_USERS:
                user = User.objects.create_user(
                    email=f'{DEMO_PREFIX}{local_part}@{domain}',
                    password=password,
                    first_name='Demo',
                    last_name=last_name,
                    profile=profile,
                    division=Division.objects.get(name=division) if division else None,
                    is_staff=is_staff,
                )

                for name in sections:
                    UserSection.objects.create(user=user, section=Section.objects.get(name=name))

                self.stdout.write(f'  {user.email:<40} {user.get_profile_display() or "TI (sin perfil)"}')

        self.stdout.write(self.style.SUCCESS(
            f'{len(DEMO_USERS)} cuentas de demostración creadas con la contraseña de '
            f'DEMO_USERS_PASSWORD.'
        ))

    def _remove(self, existing) -> None:
        ids = list(existing.values_list('id', flat=True))

        # what the demo accounts left behind would block their deletion
        MonthlyCut.objects.filter(taken_by_id__in=ids).update(taken_by=None)
        UserSection.objects.filter(user_id__in=ids).delete()
        existing.delete()
        # after the deletes, which write their own "deleted" history rows
        UserSection.history.filter(user_id__in=ids).delete()
        User.history.filter(id__in=ids).delete()
