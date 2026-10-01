# external libraries imports
from django.db.models import QuerySet

# internal application code imports
from users.access.EmployeeFieldPolicy import EmployeeFieldPolicy
from users.access.EmployeeScopePolicy import EmployeeScopePolicy


# main class
# a view that overrides get_queryset() without calling super() skips the row scope
class EmployeeScopedMixin:
    division_lookup: str = 'division'
    section_lookup: str = 'section'

    def get_queryset(self) -> QuerySet:
        queryset = super().get_queryset()
        return EmployeeScopePolicy.scope(
            self.request.user,
            queryset,
            self.division_lookup,
            self.section_lookup,
        )


# without a request in the context every field but the id is dropped
class EmployeeFieldsMixin:
    def get_fields(self) -> dict:
        request = self.context.get('request')
        readable = EmployeeFieldPolicy.readable_fields(getattr(request, 'user', None))

        return {
            name: field
            for name, field in super().get_fields().items()
            if name == 'id' or name in readable
        }
