# external libraries imports
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

# internal application code imports
from users.models import Department, User


# main code
# for Human Resources and IT only; end users work through the frontend
@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'is_active']
    list_filter = ['is_active']
    search_fields = ['code', 'name']
    ordering = ['name']


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    fieldsets = DjangoUserAdmin.fieldsets + (
        ('Departamento', {'fields': ('department',)}),
    )
    add_fieldsets = DjangoUserAdmin.add_fieldsets + (
        ('Departamento', {'fields': ('department',)}),
    )
    list_display = ['username', 'first_name', 'last_name', 'department', 'is_active']
    list_filter = DjangoUserAdmin.list_filter + ('department',)
    list_select_related = ['department']
