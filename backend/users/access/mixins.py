# external libraries imports
from django.db.models import QuerySet

# internal application code imports
from users.access.FieldAccessPolicy import FieldAccessPolicy


# main class
# Narrows the queryset for performance, NOT for security: Django silently reloads a deferred field on access. The serializer is the real boundary (6.3).
class FieldRestrictedMixin:
    def get_queryset(self) -> QuerySet:
        queryset = super().get_queryset()
        allowed = FieldAccessPolicy.allowed_fields(self.request.user, queryset.model)
        return queryset.only(*allowed)
