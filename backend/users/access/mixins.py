# external libraries imports
from django.db.models import QuerySet

# internal application code imports
from users.access.FieldAccessPolicy import FieldAccessPolicy


# main class
class FieldRestrictedMixin:
    """Acota el queryset de una vista a los campos que el usuario tiene autorizados.

    Se usa en lugar de Model.objects.all() para que ningún endpoint traiga de la base
    un campo que después habría que confiar en no serializar (6.3).
    """

    def get_queryset(self) -> QuerySet:
        queryset = super().get_queryset()
        allowed = FieldAccessPolicy.allowed_fields(self.request.user, queryset.model)
        return queryset.only(*allowed)
