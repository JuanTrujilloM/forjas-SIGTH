# external libraries imports
import io
import random
import unicodedata
from datetime import date, timedelta
from decimal import Decimal

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone
from PIL import Image, ImageDraw, ImageFont

# internal application code imports
from employees.enums import (
    AdditionalRole,
    Area,
    BloodType,
    ContractType,
    EducationLevel,
    EmployeeCategory,
    EmployeeStatus,
    EmploymentType,
    Ethnicity,
    EvaluationGroup,
    FamilyComposition,
    HealthInsurer,
    IdentificationType,
    MaritalStatus,
    OccupationalRiskInsurer,
    PensionFund,
    SalaryType,
    SeveranceFund,
    Sex,
)
from employees.models import ContractExtension, CostCenter, Employee, Position
from employees.services import EmployeePhotoService
from users.models import Division, Section

from ._demo_roster import (
    CITIES,
    COLOMBIAN_BIRTHPLACES,
    DEGREES,
    FEMALE_NAMES,
    MALE_NAMES,
    NEIGHBORHOODS,
    NOTES,
    ROSTER,
    SURNAMES,
    VENEZUELAN_BIRTHPLACES,
)

# main code
# a reserved id range, far from real documents, so --replace deletes only demo rows
DEMO_FIRST_ID = 9_000_000_001
DEMO_LAST_ID = 9_000_009_999

PHOTO_COLORS = ['#003064', '#ff8300', '#3dac2b', '#54595f', '#7a3e9d', '#c92717', '#0f766e']

AGE_RANGES = {
    'executive': (50, 64),
    'director': (40, 60),
    'leader': (30, 56),
    'analyst': (23, 50),
    'commercial': (25, 48),
    'operative': (19, 63),
    'apprentice': (17, 20),
}

HIRE_YEARS = {
    'executive': (2006, 2018),
    'director': (2008, 2021),
    'leader': (2010, 2023),
    'analyst': (2014, 2025),
    'commercial': (2016, 2025),
    'operative': (2010, 2026),
}

SALARY_RANGES = {
    'executive': (19_000_000, 26_000_000),
    'director': (12_000_000, 17_000_000),
    'leader': (5_500_000, 9_500_000),
    'analyst': (2_900_000, 4_800_000),
    'commercial': (3_200_000, 4_600_000),
    'operative': (1_900_000, 2_900_000),
    'apprentice': (1_300_000, 1_300_000),
}

EDUCATION = {
    'executive': [EducationLevel.MASTERS, EducationLevel.POSTGRADUATE],
    'director': [EducationLevel.MASTERS, EducationLevel.POSTGRADUATE],
    'leader': [EducationLevel.POSTGRADUATE, EducationLevel.PROFESSIONAL_COMPLETE,
               EducationLevel.TECHNOLOGIST_COMPLETE],
    'analyst': [EducationLevel.PROFESSIONAL_COMPLETE, EducationLevel.TECHNOLOGIST_COMPLETE,
                EducationLevel.PROFESSIONAL_INCOMPLETE],
    'commercial': [EducationLevel.PROFESSIONAL_COMPLETE, EducationLevel.TECHNOLOGIST_COMPLETE],
    'operative': [EducationLevel.HIGH_SCHOOL_COMPLETE, EducationLevel.HIGH_SCHOOL_COMPLETE,
                  EducationLevel.TECHNICAL_COMPLETE, EducationLevel.HIGH_SCHOOL_INCOMPLETE,
                  EducationLevel.PRIMARY_COMPLETE, EducationLevel.TECHNICAL_INCOMPLETE],
    'apprentice': [EducationLevel.HIGH_SCHOOL_COMPLETE, EducationLevel.TECHNICAL_INCOMPLETE],
}

DEGREE_GROUP = {
    EducationLevel.MASTERS: 'masters',
    EducationLevel.POSTGRADUATE: 'postgraduate',
    EducationLevel.PROFESSIONAL_COMPLETE: 'professional',
    EducationLevel.PROFESSIONAL_INCOMPLETE: 'professional',
    EducationLevel.TECHNOLOGIST_COMPLETE: 'technologist',
    EducationLevel.TECHNICAL_COMPLETE: 'technical',
    EducationLevel.TECHNICAL_INCOMPLETE: 'technical',
    EducationLevel.HIGH_SCHOOL_COMPLETE: 'bachelor',
}

AREA_BY_DIVISION = {
    'Dir. Administrativa, Financiera y TI': Area.ADMON_51,
    'Dir. Manufactura y Planeación': Area.MOD_72,
    'Dir. Mercadeo y Ventas': Area.VENTAS_52,
    'Dir. Operaciones': Area.LOG_52,
    'Dir. Procesos Técnicos': Area.CIF_73,
}

COST_CENTERS_BY_AREA = {
    Area.ADMON_51: ['PCOFB20000', 'PCOFB20114', 'PCOFB20300'],
    Area.MOD_72: ['PCOFB30200', 'PCOFB30201', 'PCOFB30202', 'PCOFB30203', 'PCOFB30205',
                  'PCOFB30206'],
    Area.CIF_73: ['PCOFB30300', 'PCOFB30500', 'PCOFB30503'],
    Area.LOG_52: ['PCOFB40100', 'PCOFB40400'],
    Area.VENTAS_52: ['PCOFB50103', 'PCOFB50302', 'PCOFB50400'],
}

OPERATIVE_CATEGORY = {
    'Dir. Administrativa, Financiera y TI': EmployeeCategory.OPERATIVE_ADMINISTRATIVE,
    'Dir. Manufactura y Planeación': EmployeeCategory.OPERATIVE_MANUFACTURING,
    'Dir. Operaciones': EmployeeCategory.OPERATIVE_SUPPLY,
    'Dir. Procesos Técnicos': EmployeeCategory.OPERATIVE_TECHNICAL,
}

EVALUATION_GROUP = {
    'executive': EvaluationGroup.DIRECTOR,
    'director': EvaluationGroup.DIRECTOR,
    'leader': EvaluationGroup.LEADER,
    'analyst': EvaluationGroup.ANALYST,
    'commercial': EvaluationGroup.COMMERCIAL,
    'operative': EvaluationGroup.OPERATIVE,
    'apprentice': EvaluationGroup.OPERATIVE,
}

CONTRACT_MONTHS = {
    ContractType.FIXED_THREE_MONTHS: 3,
    ContractType.FIXED_SIX_MONTHS: 6,
    ContractType.FIXED_ONE_YEAR: 12,
    ContractType.FIXED_SPECIAL: 12,
}

TRANSPORT_ALLOWANCE = Decimal('200000')
TRANSPORT_ALLOWANCE_CEILING = 3_600_000


def add_months(start: date, months: int) -> date:
    month_index = start.month - 1 + months
    year = start.year + month_index // 12
    month = month_index % 12 + 1
    day = min(start.day, 28)

    return date(year, month, day)


def ascii_slug(text: str) -> str:
    normalized = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode()
    return normalized.lower().replace(' ', '')


class Command(BaseCommand):
    help = 'Crea empleados de demostración con datos inventados. Solo en desarrollo (DEBUG=True).'

    def add_arguments(self, parser):
        parser.add_argument(
            '--replace',
            action='store_true',
            help='Borra antes los empleados de demostración que ya existan (y sus fotos).',
        )
        parser.add_argument('--seed', type=int, default=2026, help='Semilla aleatoria.')

    def handle(self, *args, **options):
        if not settings.DEBUG:
            raise CommandError('Los datos de demostración solo se cargan con DEBUG=True.')

        demo = Employee.objects.filter(id_number__range=(DEMO_FIRST_ID, DEMO_LAST_ID))

        if demo.exists() and not options['replace']:
            raise CommandError(
                f'Ya hay {demo.count()} empleados de demostración. Usa --replace para recrearlos.'
            )

        self.random = random.Random(options['seed'])
        self.today = timezone.localdate()
        self.used_names: set[str] = set()
        self.stored_photos: list[str] = []

        try:
            with transaction.atomic():
                if options['replace']:
                    self._remove_demo(demo)

                created = self._create_roster()
        except Exception:
            for name in self.stored_photos:
                default_storage.delete(name)
            raise

        retired = sum(1 for employee in created if employee.status == EmployeeStatus.RETIRED)
        self.stdout.write(self.style.SUCCESS(
            f'{len(created)} empleados de demostración creados ({retired} retirados, '
            f'{len(self.stored_photos)} con foto).'
        ))

    def _remove_demo(self, demo) -> None:
        ids = list(demo.values_list('id', flat=True))
        photos = {
            record.photo
            for record in Employee.history.filter(id__in=ids)
            if record.photo
        }

        ContractExtension.objects.filter(employee_id__in=ids).delete()
        demo.update(immediate_boss=None)
        demo.delete()
        # after the deletes, which write their own "deleted" history rows
        ContractExtension.history.filter(employee_id__in=ids).delete()
        Employee.history.filter(id__in=ids).delete()

        files = photos | {EmployeePhotoService.thumbnail_name(name) for name in photos}
        transaction.on_commit(lambda: [default_storage.delete(name) for name in files])

    def _create_roster(self) -> list[Employee]:
        divisions = {division.name: division for division in Division.objects.all()}
        sections = {section.name: section for section in Section.objects.all()}
        self.cost_centers = {center.code: center for center in CostCenter.objects.all()}
        positions = {
            name: Position.objects.get_or_create(name=name)[0]
            for name in {row[1] for row in ROSTER}
        }

        retirable = [row[0] for row in ROSTER if row[4] in ('operative', 'analyst')]
        retired_keys = set(self.random.sample(retirable, 5))
        foreign_keys = set(self.random.sample(retirable, 4))
        noted_keys = set(self.random.sample([row[0] for row in ROSTER], len(NOTES)))
        notes = iter(NOTES)

        by_key: dict[str, Employee] = {}
        section_positions: dict[str, list[Position]] = {}

        for index, (key, position_name, division_name, section_name, role, boss_key) in enumerate(ROSTER):
            employee = self._build(
                index=index,
                role=role,
                position=positions[position_name],
                division=divisions[division_name] if division_name else None,
                section=sections[section_name],
                boss=by_key.get(boss_key),
                is_foreign=key in foreign_keys,
                is_retired=key in retired_keys,
                note=next(notes) if key in noted_keys else '',
                previous_candidates=section_positions.get(section_name, []),
            )
            employee.save()
            self._add_extensions(employee)

            by_key[key] = employee
            section_positions.setdefault(section_name, []).append(positions[position_name])

        self._bring_contract_ends_near(list(by_key.values()))

        return list(by_key.values())

    # fixed offsets, not drawn, so the contract alerts always have an expired and a near case
    def _bring_contract_ends_near(self, employees: list[Employee]) -> None:
        candidates = [
            employee for employee in employees
            if employee.status == EmployeeStatus.ACTIVE
            and employee.contract_type in CONTRACT_MONTHS
        ]

        for employee, days in zip(candidates[::3], [-6, 3, 12, 27, 41]):
            employee.contract_end_date = self.today + timedelta(days=days)
            employee.save(update_fields=['contract_end_date', 'updated_at'])

    def _build(self, *, index, role, position, division, section, boss, is_foreign, is_retired,
               note, previous_candidates) -> Employee:
        rnd = self.random
        sex = rnd.choices([Sex.MALE, Sex.FEMALE], weights=[80, 20] if role == 'operative' else [50, 50])[0]
        first_name, full_name = self._name(sex)

        low, high = AGE_RANGES[role]
        age = rnd.randint(low, high)
        birth_date = self.today - timedelta(days=age * 365 + rnd.randint(0, 364))

        if role == 'apprentice':
            hire_date = self.today - timedelta(days=rnd.randint(30, 300))
        else:
            first_year, last_year = HIRE_YEARS[role]
            earliest = max(date(first_year, 1, 1), add_months(birth_date, 18 * 12))
            latest = min(date(last_year, 12, 31), self.today - timedelta(days=20))
            hire_date = earliest + timedelta(days=rnd.randint(0, max((latest - earliest).days, 0)))

        if is_foreign:
            id_type = rnd.choice([IdentificationType.CE, IdentificationType.PPT])
        elif role == 'apprentice' and age < 18:
            id_type = IdentificationType.TI
        else:
            id_type = IdentificationType.CC

        marital_status = self._marital_status(age)
        has_children = age > 24 and rnd.random() < (0.75 if age > 32 else 0.35)
        dependents = rnd.randint(1, 3) if has_children else rnd.choice([0, 0, 0, 1])

        education_level = rnd.choice(EDUCATION[role])
        degree_group = DEGREE_GROUP.get(education_level)
        degree_title = rnd.choice(DEGREES[degree_group]) if degree_group else ''

        employment_type, contract_type = self._contract(role)
        salary_type = {
            'executive': SalaryType.INTEGRAL,
            'director': SalaryType.INTEGRAL,
            'apprentice': SalaryType.APPRENTICE_SUPPORT,
        }.get(role, SalaryType.BASIC)
        low_salary, high_salary = SALARY_RANGES[role]
        salary = Decimal(rnd.randint(low_salary // 10_000, high_salary // 10_000) * 10_000)
        area = AREA_BY_DIVISION.get(division.name if division else '', Area.ADMON_51)

        previous_position = None
        previous_start = previous_end = None
        position_start = hire_date

        lower_positions = [candidate for candidate in previous_candidates if candidate != position]
        if role in ('leader', 'analyst', 'operative') and lower_positions and rnd.random() < 0.4:
            months_before = rnd.randint(8, 60)
            position_start = min(add_months(hire_date, months_before), self.today - timedelta(days=30))
            if position_start > hire_date:
                previous_position = rnd.choice(lower_positions)
                previous_start = hire_date
                previous_end = position_start - timedelta(days=1)
            else:
                position_start = hire_date

        contract_end_date = None
        if contract_type in CONTRACT_MONTHS:
            contract_end_date = add_months(hire_date, CONTRACT_MONTHS[contract_type])
        elif contract_type == ContractType.WORK_AND_LABOR:
            contract_end_date = self.today + timedelta(days=rnd.randint(20, 240))

        # derived from the index, not drawn: drawing would shift every employee generated after
        retirement_date = None
        if is_retired:
            retirement_date = max(hire_date, self.today - timedelta(days=(index * 37) % 330 + 5))

        employee = Employee(
            status=EmployeeStatus.RETIRED if is_retired else EmployeeStatus.ACTIVE,
            id_type=id_type,
            id_number=DEMO_FIRST_ID + index,
            full_name=full_name,
            birth_date=birth_date,
            sex=sex,
            blood_type=rnd.choices(
                list(BloodType),
                weights=[25, 2, 8, 1, 3, 1, 58, 2],
            )[0],
            marital_status=marital_status,
            has_children=has_children,
            mobile_phone=f'3{rnd.choice(["00", "01", "04", "10", "13", "14", "15", "20", "21"])}'
                         f'{rnd.randint(1_000_000, 9_999_999)}',
            personal_email=f'{ascii_slug(first_name)}.{ascii_slug(full_name.split()[0])}'
                           f'{rnd.randint(1, 99)}@example.com',
            address=f'{rnd.choice(["Calle", "Carrera", "Diagonal", "Transversal", "Circular"])} '
                    f'{rnd.randint(1, 120)} # {rnd.randint(1, 99)}-{rnd.randint(1, 99)}',
            neighborhood=rnd.choice(NEIGHBORHOODS),
            city=rnd.choice(CITIES),
            education_level=education_level,
            degree_title=degree_title,
            employment_type=employment_type,
            category=self._category(role, division),
            division=division,
            evaluation_group=EVALUATION_GROUP[role],
            collective_agreement=role == 'operative' and rnd.random() < 0.8,
            position=position,
            position_start_date=position_start,
            previous_position=previous_position,
            previous_position_start_date=previous_start,
            previous_position_end_date=previous_end,
            is_leader=role in ('executive', 'director', 'leader'),
            section=section,
            cost_center=self.cost_centers[rnd.choice(COST_CENTERS_BY_AREA[area])],
            area=area,
            additional_role=self._additional_role(role, section.name),
            immediate_boss=boss,
            hire_date=hire_date,
            retirement_date=retirement_date,
            current_salary=salary,
            salary_type=salary_type,
            transport_allowance=(
                TRANSPORT_ALLOWANCE
                if salary <= TRANSPORT_ALLOWANCE_CEILING and role != 'apprentice'
                else None
            ),
            contract_type=contract_type,
            contract_end_date=contract_end_date,
            occupational_risk_insurer=rnd.choices(
                [OccupationalRiskInsurer.SURA, OccupationalRiskInsurer.SEGUROS_BOLIVAR],
                weights=[85, 15],
            )[0],
            health_insurer=rnd.choices(
                [HealthInsurer.SURA, HealthInsurer.NUEVA_EPS, HealthInsurer.SANITAS,
                 HealthInsurer.SALUD_TOTAL, HealthInsurer.SAVIA_SALUD, HealthInsurer.COMPENSAR,
                 HealthInsurer.COOSALUD, HealthInsurer.ADRES],
                weights=[40, 18, 10, 10, 10, 5, 4, 3],
            )[0],
            pension_fund=(
                PensionFund.PENSIONER
                if age >= 62
                else rnd.choice([PensionFund.PORVENIR, PensionFund.PROTECCION,
                                 PensionFund.COLPENSIONES, PensionFund.SKANDIA,
                                 PensionFund.COLFONDOS])
            ),
            severance_fund=rnd.choice(list(SeveranceFund)),
            notes=note,
            birth_municipality=rnd.choice(
                VENEZUELAN_BIRTHPLACES if is_foreign else COLOMBIAN_BIRTHPLACES
            ),
            nationality='Venezolana' if is_foreign else 'Colombiana',
            ethnicity=rnd.choices(
                [Ethnicity.NONE, Ethnicity.AFRO_COLOMBIAN, Ethnicity.UNDISCLOSED,
                 Ethnicity.INDIGENOUS, Ethnicity.ROMA],
                weights=[78, 12, 8, 1, 1],
            )[0],
            family_composition=self._family_composition(age, marital_status, has_children),
            dependents_count=dependents,
            socioeconomic_stratum=self._stratum(role),
        )

        if rnd.random() < 0.75:
            self._attach_photo(employee, first_name, full_name)

        return employee

    def _name(self, sex: str) -> tuple[str, str]:
        names = FEMALE_NAMES if sex == Sex.FEMALE else MALE_NAMES

        while True:
            first_name = self.random.choice(names)
            surnames = ' '.join(self.random.sample(SURNAMES, 2))
            full_name = f'{surnames} {first_name}'

            if full_name not in self.used_names:
                self.used_names.add(full_name)
                return first_name, full_name

    def _marital_status(self, age: int) -> str:
        if age < 24:
            return MaritalStatus.SINGLE

        return self.random.choices(
            list(MaritalStatus),
            weights=[30, 35, 25, 7, 3 if age > 50 else 0],
        )[0]

    def _contract(self, role: str) -> tuple[str, str]:
        rnd = self.random

        if role == 'apprentice':
            return EmploymentType.DIRECT, ContractType.FIXED_SPECIAL

        if role in ('executive', 'director', 'leader'):
            return EmploymentType.DIRECT, ContractType.INDEFINITE

        if role in ('analyst', 'commercial'):
            return EmploymentType.DIRECT, rnd.choices(
                [ContractType.INDEFINITE, ContractType.FIXED_ONE_YEAR], weights=[70, 30]
            )[0]

        if rnd.random() < 0.15:
            return (
                rnd.choice([EmploymentType.TEMPORARY_AD, EmploymentType.TEMPORARY_SAI]),
                ContractType.WORK_AND_LABOR,
            )

        return EmploymentType.DIRECT, rnd.choices(
            [ContractType.INDEFINITE, ContractType.FIXED_ONE_YEAR, ContractType.FIXED_SIX_MONTHS,
             ContractType.FIXED_THREE_MONTHS],
            weights=[55, 25, 12, 8],
        )[0]

    def _category(self, role: str, division: Division | None) -> str:
        if role == 'apprentice':
            return self.random.choice([
                EmployeeCategory.PRODUCTION_APPRENTICE, EmployeeCategory.PRODUCTION_APPRENTICE_AD,
            ])

        if role == 'commercial':
            return EmployeeCategory.COMMERCIAL

        if role == 'operative':
            return OPERATIVE_CATEGORY.get(division.name, EmployeeCategory.OPERATIVE_ADMINISTRATIVE)

        return EmployeeCategory.ADMINISTRATIVE

    def _additional_role(self, role: str, section_name: str) -> str:
        rnd = self.random

        if section_name in ('Almacenes', 'Logística', 'Logística Interna', 'Despachos y Empaque'):
            if rnd.random() < 0.5:
                return AdditionalRole.FORKLIFT_OPERATOR

        return rnd.choices(
            [AdditionalRole.NONE, AdditionalRole.BRIGADIER, AdditionalRole.COPASST,
             AdditionalRole.COEXISTENCE_COMMITTEE],
            weights=[70, 14, 9, 7] if role != 'apprentice' else [100, 0, 0, 0],
        )[0]

    def _family_composition(self, age: int, marital_status: str, has_children: bool) -> str:
        with_partner = marital_status in (MaritalStatus.MARRIED, MaritalStatus.COMMON_LAW)

        if has_children:
            return FamilyComposition.WITH_CHILDREN

        if with_partner:
            return FamilyComposition.WITH_PARTNER

        if age < 28:
            return FamilyComposition.WITH_PARENTS

        return self.random.choice([
            FamilyComposition.LIVES_ALONE, FamilyComposition.WITH_OTHER_RELATIVES,
            FamilyComposition.WITH_NON_RELATIVES, FamilyComposition.OTHER,
        ])

    def _stratum(self, role: str) -> int:
        ranges = {
            'executive': (4, 6),
            'director': (4, 6),
            'leader': (3, 5),
            'analyst': (2, 4),
            'commercial': (2, 4),
        }
        low, high = ranges.get(role, (1, 3))

        return self.random.randint(low, high)

    def _add_extensions(self, employee: Employee) -> None:
        months = CONTRACT_MONTHS.get(employee.contract_type)

        if months is None or employee.contract_end_date is None:
            return

        # a retired employee keeps the contract end that was never renewed
        if employee.status == EmployeeStatus.RETIRED:
            return

        end = employee.contract_end_date
        renewals = 0

        while end < self.today:
            ContractExtension.objects.create(
                employee=employee, extension_date=end + timedelta(days=1)
            )
            renewals += 1
            end = add_months(end, 12 if renewals >= 3 else months)

        if end != employee.contract_end_date:
            employee.contract_end_date = end
            employee.save(update_fields=['contract_end_date', 'updated_at'])

    def _attach_photo(self, employee: Employee, first_name: str, full_name: str) -> None:
        initials = f'{first_name[0]}{full_name[0]}'.upper()
        image = Image.new('RGB', (240, 300), self.random.choice(PHOTO_COLORS))
        draw = ImageDraw.Draw(image)
        font = ImageFont.load_default(size=96)
        left, top, right, bottom = draw.textbbox((0, 0), initials, font=font)
        position = ((240 - (right - left)) / 2 - left, (300 - (bottom - top)) / 2 - top)
        draw.text(position, initials, fill='white', font=font)

        buffer = io.BytesIO()
        image.save(buffer, 'PNG')
        employee.photo.save('photo.png', ContentFile(buffer.getvalue()), save=False)
        self.stored_photos.append(employee.photo.name)
