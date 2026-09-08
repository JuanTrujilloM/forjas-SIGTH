# external libraries imports
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

# internal application code imports
from users.models import Division, User


# main code
@admin.register(Division)
class DivisionAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'is_active', 'has_full_employee_access']
    list_filter = ['is_active', 'has_full_employee_access']
    search_fields = ['code', 'name']
    ordering = ['name']

@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Información personal', {'fields': ('first_name', 'last_name')}),
        ('Dirección', {'fields': ('division',)}),
        ('Permisos', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Fechas', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'division'),
        }),
    )
    list_display = ['email', 'first_name', 'last_name', 'division', 'is_active']
    list_filter = ['is_active', 'is_staff', 'is_superuser', 'division']
    search_fields = ['email', 'first_name', 'last_name']
    ordering = ['email']
    list_select_related = ['division']
