# external libraries imports
from datetime import date

from django.utils import timezone
from rest_framework.exceptions import ValidationError
from rest_framework.generics import GenericAPIView
from rest_framework.request import Request
from rest_framework.response import Response

# internal application code imports
from employees.models import Employee, EmployeeSnapshot, MonthlyCut
from employees.services import EmployeeIndicatorService, EmployeeRowService
from users.access import EmployeeFieldPolicy, EmployeeScopedMixin, EmployeeScopePolicy


# main class
# live rows come from get_queryset(); a past month comes from its cut, scoped as it was then
class IndicatorView(EmployeeScopedMixin, GenericAPIView):
    queryset = Employee.objects.all()
    pagination_class = None
    CURRENT = 'actual'

    def get(self, request: Request) -> Response:
        result = self._indicators(request)

        return Response({
            'period': result['period'],
            'compare': result['compare'],
            'periods': result['periods'],
            'indicators': result['indicators'],
        })

    def _indicators(self, request: Request) -> dict:
        user = request.user
        readable = EmployeeFieldPolicy.readable_fields(user)
        filters = {field: request.query_params.get(field)
                   for field in EmployeeIndicatorService.FILTER_FIELDS}
        today = timezone.localdate()
        cuts = list(MonthlyCut.objects.order_by('cut_date'))

        snapshots: dict[int, list[dict]] = {cut.id: [] for cut in cuts}
        scoped = EmployeeScopePolicy.scope(user, EmployeeSnapshot.objects.all())
        for cut_id, data in scoped.values_list('cut_id', 'data'):
            snapshots[cut_id].append(data)

        def rows_of(period: str) -> tuple[date, list[dict], str]:
            if period == self.CURRENT:
                employees = EmployeeRowService.prepare(self.get_queryset())
                rows = [EmployeeRowService.row(employee, today) for employee in employees]
                return today, rows, 'Hoy'

            cut = next((cut for cut in cuts if str(cut.id) == period), None)

            if cut is None:
                raise ValidationError({'period': ['Ese corte no existe.']})

            label = f'Corte de {EmployeeIndicatorService.month_label(cut.cut_date)}'
            return cut.cut_date, snapshots[cut.id], label

        def filtered(rows: list[dict]) -> list[dict]:
            return EmployeeIndicatorService.apply_filters(rows, filters, readable)

        period = request.query_params.get('period') or self.CURRENT
        on, rows, label = rows_of(period)

        compare_value = request.query_params.get('compare')
        if compare_value is None:
            earlier = [cut for cut in cuts if cut.cut_date < on]
            compare_value = str(earlier[-1].id) if earlier else ''

        compare = None
        if compare_value and compare_value != period:
            compare_on, compare_rows, compare_label = rows_of(compare_value)
            compare = {'value': compare_value, 'label': compare_label,
                       'on': compare_on, 'rows': filtered(compare_rows)}

        history = [(cut.cut_date, filtered(snapshots[cut.id])) for cut in cuts
                   if cut.cut_date <= on]
        if period == self.CURRENT:
            history.append((today, filtered(rows)))

        rows = filtered(rows)
        indicators = EmployeeIndicatorService.compute(
            readable, rows, on, history,
            (compare['on'], compare['rows']) if compare else None,
        )

        return {
            'period': {'value': period, 'label': label, 'on': on},
            'compare': {'value': compare['value'], 'label': compare['label'], 'on': compare['on']}
            if compare else None,
            'periods': [{'value': self.CURRENT, 'label': 'Hoy'}] + [
                {'value': str(cut.id),
                 'label': f'Corte de {EmployeeIndicatorService.month_label(cut.cut_date)}'}
                for cut in reversed(cuts)
            ],
            'indicators': indicators,
            'row_count': len(rows),
        }
