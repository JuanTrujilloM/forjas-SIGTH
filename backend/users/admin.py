# external libraries imports
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.core.exceptions import ValidationError
from django.forms.models import BaseInlineFormSet
from simple_history.admin import SimpleHistoryAdmin

# internal application code imports
from users.enums import AccessProfile
from users.models import Division, Section, User, UserSection


# main code
@admin.register(Division)
class DivisionAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name']
    ordering = ['name']


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name']
    ordering = ['name']


# The sections arrive in the inline, after the user form, so the rule that ties them to
# the profile can only be checked here and not in User.clean()
class UserSectionInlineFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()

        kept = [
            form for form in self.forms
            if form.cleaned_data and not form.cleaned_data.get('DELETE')
        ]
        is_leader = self.instance.profile == AccessProfile.LEADER

        if is_leader and not kept:
            raise ValidationError('Un líder debe tener al menos una sección a cargo.')

        if not is_leader and kept:
            raise ValidationError('Solo el perfil Líder tiene secciones a cargo.')


class UserSectionInline(admin.TabularInline):
    model = UserSection
    formset = UserSectionInlineFormSet
    extra = 0
    autocomplete_fields = ['section']
    verbose_name = 'Sección a cargo'
    verbose_name_plural = 'Secciones a cargo (solo para el perfil Líder)'


@admin.register(User)
class UserAdmin(SimpleHistoryAdmin, DjangoUserAdmin):
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Información personal', {'fields': ('first_name', 'last_name')}),
        ('Acceso a empleados', {'fields': ('profile', 'division')}),
        ('Permisos', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Fechas', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'profile', 'division'),
        }),
    )
    inlines = [UserSectionInline]
    list_display = ['email', 'first_name', 'last_name', 'profile', 'division', 'is_active']
    list_filter = ['is_active', 'profile', 'division', 'is_staff', 'is_superuser']
    search_fields = ['email', 'first_name', 'last_name']
    ordering = ['email']
    list_select_related = ['division']
    history_list_display = ['profile', 'division', 'is_active']
