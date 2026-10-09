# external libraries imports
from datetime import date, timedelta

from django.db.models import QuerySet
from django.utils.html import format_html, format_html_join

# internal application code imports
from employees.enums import EmployeeStatus


# main class
class ContractAlertService:
    ALERT_DAYS = 50

    # already expired contracts stay in: an active employee past the end date is the case to catch
    @staticmethod
    def pending(queryset: QuerySet, today: date) -> QuerySet:
        return queryset.filter(
            status=EmployeeStatus.ACTIVE,
            contract_end_date__isnull=False,
            contract_end_date__lte=today + timedelta(days=ContractAlertService.ALERT_DAYS),
        ).order_by('contract_end_date', 'full_name')

    @staticmethod
    def days_left(end_date: date, today: date) -> int:
        return (end_date - today).days

    @staticmethod
    def describe(days: int) -> str:
        if days < 0:
            return f'Vencido hace {-days} {"día" if days == -1 else "días"}'

        if days == 0:
            return 'Vence hoy'

        return f'Vence en {days} {"día" if days == 1 else "días"}'

    @staticmethod
    def build_email(employees: list, today: date, page_url: str) -> tuple[str, str, str]:
        days = ContractAlertService.ALERT_DAYS
        rows = [
            {
                'name': employee.full_name,
                'position': employee.position.name,
                'section': employee.section.name,
                'end': f'{employee.contract_end_date:%d/%m/%Y}',
                'status': ContractAlertService.describe(
                    ContractAlertService.days_left(employee.contract_end_date, today)
                ),
                'expired': employee.contract_end_date < today,
            }
            for employee in employees
        ]
        expired = sum(row['expired'] for row in rows)

        contracts = '1 contrato' if len(rows) == 1 else f'{len(rows)} contratos'
        subject = f'SIGTH · {contracts} en alerta de vencimiento ({today:%d/%m/%Y})'
        if expired:
            subject += f', {expired} ya {"vencido" if expired == 1 else "vencidos"}'

        intro = (
            f'Contratos de empleados activos que vencen en los próximos {days} días o que ya '
            'vencieron sin prórroga:'
        )
        text = '\n'.join([
            intro,
            '',
            *(f"- {row['name']} · {row['position']} · {row['section']} · {row['end']} · "
              f"{row['status']}" for row in rows),
            '',
            f'Detalle en el SIGTH: {page_url}' if page_url else '',
        ])

        html = format_html(
            '<p>{}</p><table cellpadding="6" style="border-collapse:collapse">'
            '<tr><th align="left">Empleado</th><th align="left">Cargo</th>'
            '<th align="left">Sección</th><th align="left">Vence</th><th align="left">Estado</th>'
            '</tr>{}</table>{}',
            intro,
            format_html_join(
                '',
                '<tr style="color:{}"><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>',
                (
                    (
                        '#b02a37' if row['expired'] else 'inherit',
                        row['name'],
                        row['position'],
                        row['section'],
                        row['end'],
                        row['status'],
                    )
                    for row in rows
                ),
            ),
            format_html('<p><a href="{}">Ver en el SIGTH</a></p>', page_url) if page_url else '',
        )

        return subject, text, html
