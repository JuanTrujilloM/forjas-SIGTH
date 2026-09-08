# external libraries imports
from django.db.models import QuerySet

# internal application code imports
from users.access.DivisionScopePolicy import DivisionScopePolicy


# main class
# Applies the scope in get_queryset(), so no route can return a record outside it (6.3):
# not the list, not the detail fetched by id, not an export. A view that overrides
# get_queryset() without calling super() steps around the policy.
class DivisionScopedMixin:
    # path from the scoped model to Division; override it when it is not a direct FK
    division_lookup: str = 'division'

    def get_queryset(self) -> QuerySet:
        queryset = super().get_queryset()
        return DivisionScopePolicy.scope(self.request.user, queryset, self.division_lookup)
