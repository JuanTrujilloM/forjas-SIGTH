# external libraries imports
import io
from decimal import Decimal

from django.http import HttpResponse
from django.utils import timezone
from openpyxl import Workbook
from openpyxl.styles import Font
from rest_framework.request import Request

# internal application code imports
from .IndicatorView import IndicatorView


# main class
class IndicatorExportView(IndicatorView):
    def get(self, request: Request) -> HttpResponse:
        result = self._indicators(request)
        workbook = Workbook()
        workbook.remove(workbook.active)

        for indicator in result['indicators']:
            sheet = workbook.create_sheet(indicator['key'][:31])
            sheet.append([indicator['title']])
            sheet['A1'].font = Font(bold=True, size=12)
            sheet.append([result['period']['label']])
            sheet.append([])

            for line in self._sheet_rows(indicator):
                sheet.append(line)

            sheet.column_dimensions['A'].width = 40

        buffer = io.BytesIO()
        workbook.save(buffer)
        response = HttpResponse(
            buffer.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )
        response['Content-Disposition'] = (
            f'attachment; filename="analitica-{timezone.localdate():%Y-%m-%d}.xlsx"'
        )

        return response

    @staticmethod
    def _sheet_rows(indicator: dict) -> list[list]:
        data = indicator['data']

        match indicator['kind']:
            case 'summary':
                lines = [['Activos', data['active']], ['Ingresos del mes', data['hires']],
                         ['Retiros del mes', data['retirements']]]
                if data['compare']:
                    lines += [[f'Activos en {data["compare"]["label"]}', data['compare']['active']],
                              ['Variación', data['compare']['difference']]]
                return lines
            case 'bar':
                return [['', 'Cantidad'], *zip(data['labels'], data['values']), ['Total', data['total']]]
            case 'line':
                return [['Mes', 'Activos'], *zip(data['labels'], data['values'])]
            case 'crosstab':
                return [['', *data['columns']], *([row['label'], *row['values']] for row in data['rows']),
                        ['Total', *data['totals']]]
            case 'table':
                money = set(data.get('money_columns', []))
                return [
                    data['columns'],
                    *([Decimal(value) if index in money else value for index, value in enumerate(row)]
                      for row in [*data['rows'], data['totals']]),
                ]
            case 'list':
                return [['Día', 'Nombre', 'Cargo y sección'],
                        *([item['day'], item['name'], item['detail']] for item in data['items'])]

        return []
