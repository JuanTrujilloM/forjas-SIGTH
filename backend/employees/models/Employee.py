# external libraries imports
from decimal import ROUND_HALF_UP, Decimal

from django.core.validators import FileExtensionValidator, RegexValidator
from django.db import models
from django.utils import timezone
from simple_history.models import HistoricalRecords

# internal application code imports
from employees.enums import (
    AdditionalRole,
    Area,
    BloodType,
    ContractType,
    CostCenter,
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
    SocioeconomicStratum,
)
from employees.services import EmployeePhotoPath
from employees.validators import EmployeePhotoValidator

from .Position import Position


# main class
class Employee(models.Model):
    # 42 weekly hours; the specification's 220 belongs to the former 44-hour week
    MONTHLY_WORK_HOURS = 210

    # fields
    id = models.AutoField(primary_key=True)
    status = models.CharField(
        max_length=20,
        choices=EmployeeStatus.choices,
        default=EmployeeStatus.ACTIVE,
        verbose_name='Estado',
        help_text='Retirar a un empleado es cambiar su estado; no se borra',
    )
    id_type = models.CharField(
        max_length=10, choices=IdentificationType.choices, verbose_name='Tipo de identificación'
    )
    id_number = models.PositiveBigIntegerField(
        unique=True,
        error_messages={'unique': 'Ya existe un empleado con esta identificación.'},
        verbose_name='Identificación',
        help_text='Único sin importar el tipo: al pasar de T.I. a cédula se conserva el registro',
    )
    full_name = models.CharField(max_length=200, verbose_name='Apellidos y nombres')
    photo = models.ImageField(
        upload_to=EmployeePhotoPath(),
        null=True,
        blank=True,
        validators=[
            FileExtensionValidator(['jpg', 'jpeg', 'png', 'webp']),
            EmployeePhotoValidator(),
        ],
        verbose_name='Foto',
        help_text='JPG, PNG o WebP de máximo 5 MB',
    )
    birth_date = models.DateField(verbose_name='Fecha de nacimiento')
    sex = models.CharField(max_length=10, choices=Sex.choices, verbose_name='Sexo')
    blood_type = models.CharField(
        max_length=15, choices=BloodType.choices, verbose_name='Grupo sanguíneo'
    )
    marital_status = models.CharField(
        max_length=20, choices=MaritalStatus.choices, verbose_name='Estado civil'
    )
    has_children = models.BooleanField(verbose_name='Tiene hijos')
    mobile_phone = models.CharField(
        max_length=20,
        validators=[RegexValidator(r'^\d+$', 'El celular solo lleva números.')],
        verbose_name='Celular',
    )
    personal_email = models.EmailField(blank=True, verbose_name='Correo electrónico')
    address = models.CharField(max_length=200, verbose_name='Dirección de residencia')
    neighborhood = models.CharField(max_length=120, verbose_name='Barrio')
    city = models.CharField(max_length=120, verbose_name='Ciudad')
    education_level = models.CharField(
        max_length=30, choices=EducationLevel.choices, verbose_name='Nivel educativo'
    )
    degree_title = models.CharField(max_length=200, blank=True, verbose_name='Título')
    employment_type = models.CharField(
        max_length=20, choices=EmploymentType.choices, verbose_name='Tipo de vinculación'
    )
    category = models.CharField(
        max_length=30, choices=EmployeeCategory.choices, verbose_name='Categoría'
    )
    evaluation_group = models.CharField(
        max_length=20, choices=EvaluationGroup.choices, verbose_name='Grupo de evaluación'
    )
    collective_agreement = models.BooleanField(verbose_name='Pacto colectivo')
    position_start_date = models.DateField(verbose_name='Fecha de inicio del cargo actual')
    previous_position_start_date = models.DateField(
        null=True, blank=True, verbose_name='Fecha de inicio del cargo anterior'
    )
    previous_position_end_date = models.DateField(
        null=True, blank=True, verbose_name='Fecha de fin del cargo anterior'
    )
    is_leader = models.BooleanField(
        verbose_name='Es líder',
        help_text='Con cargo de liderazgo o personal a cargo. No da acceso al sistema',
    )
    cost_center = models.CharField(
        max_length=20, choices=CostCenter.choices, verbose_name='Centro de costos'
    )
    area = models.CharField(max_length=20, choices=Area.choices, verbose_name='Área')
    additional_role = models.CharField(
        max_length=30, choices=AdditionalRole.choices, verbose_name='Rol adicional'
    )
    hire_date = models.DateField(verbose_name='Fecha de ingreso')
    training = models.TextField(
        blank=True, verbose_name='Formación', help_text='AROs y formaciones, en texto libre'
    )
    current_salary = models.DecimalField(
        max_digits=14, decimal_places=2, verbose_name='Salario actual'
    )
    salary_type = models.CharField(
        max_length=30, choices=SalaryType.choices, verbose_name='Tipo de salario'
    )
    transport_allowance = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True, verbose_name='Auxilio de transporte'
    )
    contract_type = models.CharField(
        max_length=30, choices=ContractType.choices, verbose_name='Tipo de contrato'
    )
    contract_end_date = models.DateField(
        null=True, blank=True, verbose_name='Fecha de vencimiento del contrato'
    )
    indefinite_extension = models.CharField(
        max_length=200, blank=True, verbose_name='Prórroga indefinido'
    )
    occupational_risk_insurer = models.CharField(
        max_length=30, choices=OccupationalRiskInsurer.choices, verbose_name='ARL'
    )
    health_insurer = models.CharField(
        max_length=30, choices=HealthInsurer.choices, verbose_name='EPS'
    )
    pension_fund = models.CharField(
        max_length=30, choices=PensionFund.choices, blank=True, verbose_name='Fondo de pensión'
    )
    severance_fund = models.CharField(
        max_length=30, choices=SeveranceFund.choices, blank=True, verbose_name='Fondo de cesantías'
    )
    notes = models.TextField(blank=True, verbose_name='Alertas / Observaciones')
    birth_municipality = models.CharField(max_length=120, verbose_name='Municipio de nacimiento')
    nationality = models.CharField(max_length=120, verbose_name='Nacionalidad')
    ethnicity = models.CharField(
        max_length=30, choices=Ethnicity.choices, verbose_name='Pertenencia étnica'
    )
    family_composition = models.CharField(
        max_length=30,
        choices=FamilyComposition.choices,
        verbose_name='Composición familiar',
    )
    dependents_count = models.PositiveSmallIntegerField(verbose_name='Número de personas a cargo')
    socioeconomic_stratum = models.PositiveSmallIntegerField(
        choices=SocioeconomicStratum.choices,
        verbose_name='Estrato socioeconómico',
    )

    # relations
    division = models.ForeignKey(
        'users.Division',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='employees',
        verbose_name='Dirección',
        help_text='Vacía para Gerencia y Junta Directiva, que no pertenecen a ninguna dirección',
    )
    section = models.ForeignKey(
        'users.Section',
        on_delete=models.PROTECT,
        related_name='employees',
        verbose_name='Sección',
    )
    position = models.ForeignKey(
        Position,
        on_delete=models.PROTECT,
        related_name='current_employees',
        verbose_name='Cargo actual',
    )
    previous_position = models.ForeignKey(
        Position,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='former_employees',
        verbose_name='Cargo anterior',
    )
    immediate_boss = models.ForeignKey(
        'self',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='direct_reports',
        verbose_name='Jefe inmediato',
    )

    # timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    history = HistoricalRecords()

    class Meta:
        ordering = ['full_name', 'id']
        verbose_name = 'Empleado'
        verbose_name_plural = 'Empleados'

    def __str__(self):
        return self.full_name

    @property
    def age(self) -> int | None:
        if self.birth_date is None:
            return None

        return self._whole_months_since(self.birth_date) // 12

    @property
    def seniority(self) -> dict[str, int] | None:
        if self.hire_date is None:
            return None

        months = self._whole_months_since(self.hire_date)

        return {'years': months // 12, 'months': months % 12}

    @property
    def hourly_rate(self) -> Decimal | None:
        if self.current_salary is None:
            return None

        return (self.current_salary / self.MONTHLY_WORK_HOURS).quantize(
            Decimal('0.01'), rounding=ROUND_HALF_UP
        )

    @staticmethod
    def _whole_months_since(start) -> int:
        today = timezone.localdate()
        months = (today.year - start.year) * 12 + today.month - start.month

        if today.day < start.day:
            months -= 1

        return max(months, 0)
