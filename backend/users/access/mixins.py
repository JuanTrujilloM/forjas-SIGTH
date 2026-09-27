# external libraries imports
from django.db.models import QuerySet

# internal application code imports
from users.access.EmployeeScopePolicy import EmployeeScopePolicy


# main class
# Applies the row scope in get_queryset(), so no route can return an employee outside it
# (6.4): not the list, not the detail fetched by id, not an export. A view that overrides
# get_queryset() without calling super() steps around the policy.
class EmployeeScopedMixin:
    # paths from the scoped model to Division and Section; override when not direct FKs
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
