# external libraries imports
from django.contrib.auth.models import AbstractBaseUser
from django.db.models import Model


# main class
# single point where field access is decided (6.3), so no endpoint can skip it
class FieldAccessPolicy:
    @staticmethod
    def allowed_fields(user: AbstractBaseUser, model: type[Model]) -> frozenset[str]:
        # PENDING (12, #5): an empty frozenset would look safe but break every
        # endpoint in silence, so this fails loudly until the matrix exists
        raise NotImplementedError(
            'FieldAccessPolicy.allowed_fields depende de la matriz de permisos (12, #5)'
        )
