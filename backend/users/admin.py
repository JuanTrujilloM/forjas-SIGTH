# external libraries imports
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

# internal application code imports
from users.models import Division, User


# main code
# for Human Resources and IT only; end users work through the frontend
@admin.register(Division)
class DivisionAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'is_active', 'has_full_employee_access']
    list_filter = ['is_active', 'has_full_employee_access']
    search_fields = ['code', 'name']
    ordering = ['name']


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    fieldsets = DjangoUserAdmin.fieldsets + (
        ('Dirección', {'fields': ('division',)}),
    )
    add_fieldsets = DjangoUserAdmin.add_fieldsets + (
        ('Dirección', {'fields': ('division',)}),
    )
    list_display = ['username', 'first_name', 'last_name', 'division', 'is_active']
    list_filter = DjangoUserAdmin.list_filter + ('division',)
    list_select_related = ['division']
