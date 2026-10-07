# external libraries imports
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.core.management.base import BaseCommand
from django.utils import timezone

# internal application code imports
from employees.models import ContractAlertDispatch, Employee
from employees.services import ContractAlertService
from users.enums import AccessProfile
from users.models import User


# main class
class Command(BaseCommand):
    help = (
        'Envía a las cuentas de Talento Humano el correo diario con los contratos que vencen '
        f'en los próximos {ContractAlertService.ALERT_DAYS} días o ya vencieron. Se programa '
        'una vez al día; si ya salió hoy, no lo repite.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--force', action='store_true', help='Lo envía aunque ya haya salido hoy.'
        )

    def handle(self, *args, **options):
        today = timezone.localdate()

        if not options['force'] and ContractAlertDispatch.objects.filter(sent_on=today).exists():
            self.stdout.write('El correo de vencimientos de hoy ya se envió.')
            return

        recipients = list(
            User.objects.filter(is_active=True, profile=AccessProfile.TALENT_MANAGEMENT)
            .order_by('email')
            .values_list('email', flat=True)
        )

        if not recipients:
            self.stderr.write('No hay cuentas activas de Talento Humano a quién enviarlo.')
            return

        employees = list(
            ContractAlertService.pending(
                Employee.objects.select_related('position', 'section'), today
            )
        )

        if employees:
            page_url = (
                f'{settings.FRONTEND_BASE_URL}/vencimientos' if settings.FRONTEND_BASE_URL else ''
            )
            subject, text, html = ContractAlertService.build_email(employees, today, page_url)
            message = EmailMultiAlternatives(subject, text, to=recipients)
            message.attach_alternative(html, 'text/html')
            message.send()

        ContractAlertDispatch.objects.update_or_create(
            sent_on=today,
            defaults={'recipients': ', '.join(recipients), 'employee_count': len(employees)},
        )

        self.stdout.write(
            f'Contratos en alerta: {len(employees)}; correo a {len(recipients)} cuentas.'
            if employees
            else 'No hay contratos en alerta; no se envió correo.'
        )
