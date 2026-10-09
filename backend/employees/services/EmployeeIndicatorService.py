# external libraries imports
from collections import Counter
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Callable

# internal application code imports
from employees.enums import (
    ContractType,
    EmployeeCategory,
    EmployeeStatus,
    EmploymentType,
    Sex,
)


# main code
APPRENTICE_CATEGORIES = {
    EmployeeCategory.PRODUCTION_APPRENTICE,
    EmployeeCategory.PRODUCTION_APPRENTICE_AD,
}

AGE_RANGES = [(None, 18, 'Menor de 18'), (18, 26, '18 a 25'), (26, 36, '26 a 35'),
              (36, 46, '36 a 45'), (46, 56, '46 a 55'), (56, None, '56 o más')]

SENIORITY_RANGES = [(0, 1, 'Menos de 1 año'), (1, 3, '1 a 3 años'), (3, 5, '3 a 5 años'),
                    (5, 10, '5 a 10 años'), (10, 20, '10 a 20 años'), (20, None, '20 años o más')]

NO_DIVISION = 'Gerencia y Junta Directiva'

SEXES = [(Sex.FEMALE, 'F'), (Sex.MALE, 'M')]

MONTHS = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto',
          'septiembre', 'octubre', 'noviembre', 'diciembre']


@dataclass(frozen=True)
class Indicator:
    key: str
    title: str
    sheet: str
    kind: str
    fields: frozenset[str]
    compute: Callable


# main class
class EmployeeIndicatorService:
    # filters on columns the profile cannot read are dropped, like the list filters
    FILTER_FIELDS = ['division', 'section', 'area', 'sex', 'employment_type', 'category']

    @staticmethod
    def month_label(day: date) -> str:
        return f'{MONTHS[day.month - 1]} de {day.year}'

    @staticmethod
    def apply_filters(rows: list[dict], filters: dict, readable: frozenset[str]) -> list[dict]:
        for field in EmployeeIndicatorService.FILTER_FIELDS:
            value = filters.get(field)

            if value in (None, '') or field not in readable:
                continue

            rows = [row for row in rows if str(row.get(field)) == str(value)]

        return rows

    @staticmethod
    def active(rows: list[dict]) -> list[dict]:
        return [row for row in rows if row['status'] == EmployeeStatus.ACTIVE]

    @staticmethod
    def compute(
        readable: frozenset[str],
        rows: list[dict],
        on: date,
        history: list[tuple[date, list[dict]]],
        compare: tuple[date, list[dict]] | None,
    ) -> list[dict]:
        context = {'on': on, 'history': history, 'compare': compare}
        indicators = [
            {
                'key': indicator.key,
                'title': indicator.title,
                'sheet': indicator.sheet,
                'kind': indicator.kind,
                'data': indicator.compute(rows, context),
            }
            for indicator in INDICATORS
            if indicator.fields <= readable
            and (indicator.key != 'variation' or compare is not None)
        ]

        return indicators


def _choice_label(choices, value) -> str:
    return dict(choices).get(value, value or 'Sin dato')


def _bar(counter: Counter, order: list[str] | None = None) -> dict:
    labels = order if order is not None else [label for label, _ in counter.most_common()]
    bar = {
        'labels': labels,
        'values': [counter.get(label, 0) for label in labels],
        'total': sum(counter.values()),
    }

    return bar


def _by_sex(rows: list[dict], label_of: Callable, order: list[str] | None = None) -> dict:
    counts: dict[str, Counter] = {}

    for row in rows:
        counts.setdefault(label_of(row), Counter())[row['sex']] += 1

    labels = order if order is not None else sorted(counts, key=lambda label: label.lower())
    table_rows = []

    for label in labels:
        counter = counts.get(label, Counter())
        values = [counter.get(sex, 0) for sex, _ in SEXES]
        table_rows.append({'label': label, 'values': [*values, sum(values)]})

    totals = [sum(row['values'][index] for row in table_rows) for index in range(len(SEXES) + 1)]
    crosstab = {
        'columns': [label for _, label in SEXES] + ['Total'],
        'rows': table_rows,
        'totals': totals,
    }

    return crosstab


def _bucket(value: int | None, ranges: list) -> str | None:
    if value is None:
        return None

    for low, high, label in ranges:
        if (low is None or value >= low) and (high is None or value < high):
            return label

    return None


def _summary(rows: list[dict], context: dict) -> dict:
    on = context['on']
    month = (on.year, on.month)

    def in_month(value: str | None) -> bool:
        return bool(value) and (int(value[:4]), int(value[5:7])) == month

    active = EmployeeIndicatorService.active(rows)
    summary = {
        'active': len(active),
        'hires': sum(1 for row in rows if in_month(row.get('hire_date'))),
        'retirements': sum(1 for row in rows if in_month(row.get('retirement_date'))),
        'month': EmployeeIndicatorService.month_label(on),
        'compare': None,
    }

    if context['compare'] is not None:
        compare_on, compare_rows = context['compare']
        previous = len(EmployeeIndicatorService.active(compare_rows))
        summary['compare'] = {
            'label': EmployeeIndicatorService.month_label(compare_on),
            'active': previous,
            'difference': len(active) - previous,
            'percent': round((len(active) - previous) * 100 / previous, 1) if previous else None,
        }

    return summary


def _employment(row: dict) -> str:
    if row['category'] in APPRENTICE_CATEGORIES:
        return 'Aprendices'

    return _choice_label(EmploymentType.choices, row['employment_type'])


def _section_salary(rows: list[dict], context: dict) -> dict:
    groups: dict[tuple, list[Decimal]] = {}

    for row in EmployeeIndicatorService.active(rows):
        key = (row['section_name'] or 'Sin sección', row['division_name'] or NO_DIVISION)
        groups.setdefault(key, []).append(Decimal(row['current_salary']))

    table_rows = [
        [section, division, len(salaries), str(sum(salaries))]
        for (section, division), salaries in sorted(groups.items())
    ]
    table = {
        'columns': ['Sección', 'Dirección', 'Cantidad', 'Suma de salario'],
        'money_columns': [3],
        'rows': table_rows,
        'totals': ['Total', '', sum(row[2] for row in table_rows),
                   str(sum(Decimal(row[3]) for row in table_rows))],
    }

    return table


def _birthdays(rows: list[dict], context: dict) -> dict:
    month = context['on'].month
    people = sorted(
        (row for row in EmployeeIndicatorService.active(rows)
         if row.get('birth_date') and int(row['birth_date'][5:7]) == month),
        key=lambda row: (int(row['birth_date'][8:10]), row['full_name']),
    )
    birthdays = {
        'month': MONTHS[month - 1],
        'items': [
            {
                'name': row['full_name'],
                'day': int(row['birth_date'][8:10]),
                'detail': ' · '.join(filter(None, [row.get('position_name'),
                                                   row.get('section_name')])),
            }
            for row in people
        ],
    }

    return birthdays


def _evolution(rows: list[dict], context: dict) -> dict:
    points = [
        (on, len(EmployeeIndicatorService.active(period_rows)))
        for on, period_rows in context['history']
    ]
    yearly: dict[int, int] = {}

    for on, count in points:
        yearly[on.year] = count

    evolution = {
        'labels': [f'{MONTHS[on.month - 1][:3]} {on.year}' for on, _ in points],
        'values': [count for _, count in points],
        'years': [{'year': year, 'active': count} for year, count in sorted(yearly.items())],
    }

    return evolution


def _variation(rows: list[dict], context: dict) -> dict:
    compare_on, compare_rows = context['compare']
    current = Counter(row['division_name'] or NO_DIVISION
                      for row in EmployeeIndicatorService.active(rows))
    previous = Counter(row['division_name'] or NO_DIVISION
                       for row in EmployeeIndicatorService.active(compare_rows))
    labels = sorted(set(current) | set(previous))
    variation = {
        'columns': ['Dirección', EmployeeIndicatorService.month_label(compare_on),
                    EmployeeIndicatorService.month_label(context['on']), 'Variación'],
        'rows': [[label, previous[label], current[label], current[label] - previous[label]]
                 for label in labels],
        'totals': ['Total', sum(previous.values()), sum(current.values()),
                   sum(current.values()) - sum(previous.values())],
    }

    return variation


def _active_counter(rows: list[dict], label_of: Callable) -> Counter:
    return Counter(label_of(row) for row in EmployeeIndicatorService.active(rows))


def _age(row: dict) -> str | None:
    return _bucket(row.get('age'), AGE_RANGES)


def _seniority(row: dict) -> str | None:
    seniority = row.get('seniority')
    return _bucket(seniority['years'] if seniority else None, SENIORITY_RANGES)


INDICATORS = [
    Indicator('summary', 'Resumen', 'Resumen', 'summary',
              frozenset({'status', 'hire_date', 'retirement_date'}), _summary),
    Indicator('evolution', 'Evolución de colaboradores activos', 'Evolución de activos', 'line',
              frozenset({'status'}), _evolution),
    Indicator('variation', 'Variación por dirección', 'Variación por dirección', 'table',
              frozenset({'status', 'division_name'}), _variation),
    Indicator('by_category', 'Personal activo por categoría', 'Por categoría', 'bar',
              frozenset({'status', 'category'}),
              lambda rows, context: _bar(_active_counter(
                  rows, lambda row: _choice_label(EmployeeCategory.choices, row['category'])))),
    Indicator('by_division', 'Personal activo por dirección', 'Por dirección', 'bar',
              frozenset({'status', 'division_name'}),
              lambda rows, context: _bar(_active_counter(
                  rows, lambda row: row['division_name'] or NO_DIVISION))),
    Indicator('by_section', 'Personal activo por sección', 'Por sección', 'bar',
              frozenset({'status', 'section_name'}),
              lambda rows, context: _bar(_active_counter(
                  rows, lambda row: row['section_name'] or 'Sin sección'))),
    Indicator('by_position', 'Personal activo por cargo', 'Por cargo', 'bar',
              frozenset({'status', 'position_name'}),
              lambda rows, context: _bar(_active_counter(
                  rows, lambda row: row['position_name'] or 'Sin cargo'))),
    Indicator('division_by_sex', 'Dirección por sexo', 'Dirección por sexo', 'crosstab',
              frozenset({'status', 'division_name', 'sex'}),
              lambda rows, context: _by_sex(
                  EmployeeIndicatorService.active(rows),
                  lambda row: row['division_name'] or NO_DIVISION)),
    Indicator('employment_by_sex', 'Vinculación por sexo', 'Vinculación por sexo', 'crosstab',
              frozenset({'status', 'employment_type', 'category', 'sex'}),
              lambda rows, context: _by_sex(
                  EmployeeIndicatorService.active(rows), _employment,
                  [label for _, label in EmploymentType.choices] + ['Aprendices'])),
    Indicator('contract_by_sex', 'Tipo de contratación por sexo', 'Contratación por sexo', 'crosstab',
              frozenset({'status', 'contract_type', 'sex'}),
              lambda rows, context: _by_sex(
                  EmployeeIndicatorService.active(rows),
                  lambda row: _choice_label(ContractType.choices, row['contract_type']),
                  [label for _, label in ContractType.choices])),
    Indicator('age_by_sex', 'Edad por sexo', 'Edad por sexo', 'crosstab',
              frozenset({'status', 'age', 'sex'}),
              lambda rows, context: _by_sex(
                  [row for row in EmployeeIndicatorService.active(rows) if _age(row)], _age,
                  [label for _, _, label in AGE_RANGES])),
    Indicator('seniority', 'Antigüedad', 'Antigüedad', 'bar',
              frozenset({'status', 'seniority'}),
              lambda rows, context: _bar(
                  Counter(label for row in EmployeeIndicatorService.active(rows)
                          if (label := _seniority(row))),
                  [label for _, _, label in SENIORITY_RANGES])),
    Indicator('collective_agreement', 'Pacto colectivo', 'Pacto colectivo', 'bar',
              frozenset({'status', 'collective_agreement'}),
              lambda rows, context: _bar(
                  _active_counter(rows, lambda row: 'Sí' if row['collective_agreement'] else 'No'),
                  ['Sí', 'No'])),
    Indicator('section_salary', 'Personal y salario por sección', 'Salario por sección', 'table',
              frozenset({'status', 'section_name', 'division_name', 'current_salary'}),
              _section_salary),
    Indicator('birthdays', 'Cumpleaños del mes', 'Cumpleaños del mes', 'list',
              frozenset({'status', 'birth_date', 'full_name', 'position_name', 'section_name'}),
              _birthdays),
]
