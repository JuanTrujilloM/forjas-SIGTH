# external libraries imports
from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

# internal application code imports
from employees.models import ContractExtension, Employee, Position
from users.access import EmployeeFieldPolicy


# main code
# Access to this part of the admin is decided by the employee policy and not by Django's
# model permissions (6.3): Talent Management edits, IT reads, nobody deletes.
class EmployeePolicyAdminMixin:
    def has_module_permission(self, request) -> bool:
        return EmployeeFieldPolicy.can_view_admin(request.user)

    def has_view_permission(self, request, obj=None) -> bool:
        return EmployeeFieldPolicy.can_view_admin(request.user)

    def has_add_permission(self, request, obj=None) -> bool:
        return EmployeeFieldPolicy.can_view_admin(request.user) and EmployeeFieldPolicy.can_write(
            request.user
        )

    def has_change_permission(self, request, obj=None) -> bool:
        return self.has_add_permission(request)

    def has_delete_permission(self, request, obj=None) -> bool:
        return False


@admin.register(Position)
class PositionAdmin(EmployeePolicyAdminMixin, admin.ModelAdmin):
    list_display = ['name', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name']
    ordering = ['name']


class ContractExtensionInline(EmployeePolicyAdminMixin, admin.TabularInline):
    model = ContractExtension
    extra = 0
    fields = ['extension_date']


@admin.register(Employee)
class EmployeeAdmin(EmployeePolicyAdminMixin, SimpleHistoryAdmin):
    fieldsets = (
        ('Identidad', {'fields': (
            'status', 'id_type', 'id_number', 'full_name', 'photo', 'birth_date', 'age', 'sex',
            'blood_type', 'marital_status',
        )}),
        ('Contacto y educación', {'fields': (
            'has_children', 'mobile_phone', 'personal_email', 'address', 'neighborhood',
            'city', 'education_level', 'degree_title',
        )}),
        ('Laboral', {'fields': (
            'employment_type', 'category', 'division', 'evaluation_group',
            'collective_agreement', 'position', 'position_start_date', 'previous_position',
            'previous_position_start_date', 'previous_position_end_date', 'is_leader',
            'section', 'cost_center', 'area', 'additional_role', 'immediate_boss', 'hire_date',
            'seniority', 'training',
        )}),
        ('Salario y contrato', {'fields': (
            'current_salary', 'salary_type', 'hourly_rate', 'transport_allowance',
            'contract_type', 'contract_end_date', 'indefinite_extension',
        )}),
        ('Salud y riesgos', {'fields': ('occupational_risk_insurer', 'health_insurer')}),
        ('Pensión y cesantías', {'fields': ('pension_fund', 'severance_fund')}),
        ('Observaciones', {'fields': ('notes',)}),
        ('Sociodemográfico', {'fields': (
            'birth_municipality', 'nationality', 'ethnicity', 'family_composition',
            'dependents_count', 'socioeconomic_stratum',
        )}),
    )
    readonly_fields = ['age', 'seniority', 'hourly_rate']
    inlines = [ContractExtensionInline]
    autocomplete_fields = ['immediate_boss']
    list_display = ['full_name', 'id_type', 'id_number', 'status', 'division', 'section', 'position']
    list_filter = ['status', 'division', 'section', 'category', 'employment_type', 'contract_type']
    search_fields = ['full_name', '=id_number']
    list_select_related = ['division', 'section', 'position']
    history_list_display = ['status', 'division', 'section', 'position']

    @admin.display(description='Edad')
    def age(self, employee: Employee) -> int | None:
        return employee.age

    @admin.display(description='Antigüedad')
    def seniority(self, employee: Employee) -> str | None:
        if employee.seniority is None:
            return None

        return f'{employee.seniority["years"]} años, {employee.seniority["months"]} meses'

    @admin.display(description='Valor hora')
    def hourly_rate(self, employee: Employee):
        return employee.hourly_rate
