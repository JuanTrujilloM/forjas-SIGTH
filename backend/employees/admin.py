# external libraries imports
from django.contrib import admin
from django.db.models import Count
from simple_history.admin import SimpleHistoryAdmin

# internal application code imports
from employees.models import (
    ContractAlertDispatch,
    ContractExtension,
    CostCenter,
    Employee,
    EmployeeExportLog,
    MonthlyCut,
    Position,
)
from users.access import EmployeeFieldPolicy


# main code
# admin access comes from the employee policy, not from Django's model permissions
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


@admin.register(CostCenter)
class CostCenterAdmin(EmployeePolicyAdminMixin, admin.ModelAdmin):
    list_display = ['code', 'name', 'is_active']
    list_filter = ['is_active']
    search_fields = ['code', 'name']
    ordering = ['code']


@admin.register(ContractAlertDispatch)
class ContractAlertDispatchAdmin(EmployeePolicyAdminMixin, admin.ModelAdmin):
    list_display = ['sent_on', 'employee_count', 'recipients', 'created_at']
    readonly_fields = ['sent_on', 'employee_count', 'recipients', 'created_at']

    def has_add_permission(self, request, obj=None) -> bool:
        return False

    def has_change_permission(self, request, obj=None) -> bool:
        return False


@admin.register(MonthlyCut)
class MonthlyCutAdmin(EmployeePolicyAdminMixin, admin.ModelAdmin):
    list_display = ['cut_date', 'employee_count', 'taken_by', 'created_at', 'updated_at']
    readonly_fields = ['cut_date', 'taken_by', 'created_at', 'updated_at']
    list_select_related = ['taken_by']

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(employee_count=Count('snapshots'))

    @admin.display(description='Empleados', ordering='employee_count')
    def employee_count(self, cut: MonthlyCut) -> int:
        return cut.employee_count

    def has_add_permission(self, request, obj=None) -> bool:
        return False

    def has_change_permission(self, request, obj=None) -> bool:
        return False


@admin.register(EmployeeExportLog)
class EmployeeExportLogAdmin(EmployeePolicyAdminMixin, admin.ModelAdmin):
    list_display = ['created_at', 'user', 'title', 'file_format', 'row_count']
    list_filter = ['file_format']
    search_fields = ['user__email', 'title']
    readonly_fields = ['created_at', 'user', 'title', 'file_format', 'row_count', 'filters', 'fields']
    list_select_related = ['user']

    def has_add_permission(self, request, obj=None) -> bool:
        return False

    def has_change_permission(self, request, obj=None) -> bool:
        return False


# read-only: an extension is registered from the frontend, which also moves the contract end date
class ContractExtensionInline(EmployeePolicyAdminMixin, admin.TabularInline):
    model = ContractExtension
    extra = 0
    fields = ['extension_date']
    readonly_fields = ['extension_date']

    def has_add_permission(self, request, obj=None) -> bool:
        return False

    def has_change_permission(self, request, obj=None) -> bool:
        return False


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
            'retirement_date', 'seniority', 'training',
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
