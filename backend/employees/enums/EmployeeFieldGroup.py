# external libraries imports
from django.db import models


# main class
class EmployeeFieldGroup(models.TextChoices):
    IDENTITY = 'identity', 'Identidad'
    CONTACT_AND_EDUCATION = 'contact_and_education', 'Contacto y educación'
    EMPLOYMENT = 'employment', 'Laboral'
    COMPENSATION_AND_CONTRACT = 'compensation_and_contract', 'Salario y contrato'
    HEALTH_AND_RISK = 'health_and_risk', 'Salud y riesgos'
    PENSION_AND_SEVERANCE = 'pension_and_severance', 'Pensión y cesantías'
    NOTES = 'notes', 'Observaciones'
    SOCIODEMOGRAPHIC = 'sociodemographic', 'Sociodemográfico'


# a field left out of every group is readable by nobody
EMPLOYEE_FIELD_GROUPS: dict[EmployeeFieldGroup, frozenset[str]] = {
    EmployeeFieldGroup.IDENTITY: frozenset({
        'status',
        'id_type',
        'id_number',
        'full_name',
        'photo',
        'photo_thumbnail',
        'birth_date',
        'age',
        'sex',
        'blood_type',
        'marital_status',
    }),
    EmployeeFieldGroup.CONTACT_AND_EDUCATION: frozenset({
        'has_children',
        'mobile_phone',
        'personal_email',
        'address',
        'neighborhood',
        'city',
        'education_level',
        'degree_title',
    }),
    EmployeeFieldGroup.EMPLOYMENT: frozenset({
        'employment_type',
        'category',
        'division',
        'division_name',
        'evaluation_group',
        'collective_agreement',
        'position',
        'position_name',
        'position_start_date',
        'previous_position',
        'previous_position_name',
        'previous_position_start_date',
        'previous_position_end_date',
        'is_leader',
        'section',
        'section_name',
        'cost_center',
        'cost_center_code',
        'cost_center_name',
        'area',
        'additional_role',
        'immediate_boss',
        'immediate_boss_name',
        'hire_date',
        'retirement_date',
        'seniority',
        'training',
    }),
    EmployeeFieldGroup.COMPENSATION_AND_CONTRACT: frozenset({
        'current_salary',
        'salary_type',
        'hourly_rate',
        'transport_allowance',
        'contract_type',
        'contract_end_date',
        'extensions',
        'indefinite_extension',
    }),
    EmployeeFieldGroup.HEALTH_AND_RISK: frozenset({
        'occupational_risk_insurer',
        'health_insurer',
    }),
    EmployeeFieldGroup.PENSION_AND_SEVERANCE: frozenset({
        'pension_fund',
        'severance_fund',
    }),
    EmployeeFieldGroup.NOTES: frozenset({
        'notes',
    }),
    EmployeeFieldGroup.SOCIODEMOGRAPHIC: frozenset({
        'birth_municipality',
        'nationality',
        'ethnicity',
        'family_composition',
        'dependents_count',
        'socioeconomic_stratum',
    }),
}
