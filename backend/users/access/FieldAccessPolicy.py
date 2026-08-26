# external libraries imports
from django.contrib.auth.models import AbstractBaseUser
from django.db.models import Model


# main class
class FieldAccessPolicy:
    """Resuelve qué campos puede ver un usuario; punto único de aplicación (6.3).

    Vive aquí y no en cada vista para que exista un solo lugar donde se decida el
    acceso por campo, y para que la auditoría de lectura (11.3) quede garantizada
    sin depender de que cada endpoint se acuerde de registrarla.
    """

    @staticmethod
    def allowed_fields(user: AbstractBaseUser, model: type[Model]) -> frozenset[str]:
        """Devuelve los campos del modelo que el usuario puede leer.

        HR_ADMIN se resuelve antes de consultar la matriz, con acceso total; el resto
        se resuelve por el code del Department contra FIELD_ACCESS_MATRIX.
        """
        # PENDING (14, #5): reads FIELD_ACCESS_MATRIX once the matrix and the
        # User/Department models exist. Returning an empty frozenset would look safe
        # but silently break every endpoint, so this fails loudly instead.
        raise NotImplementedError(
            'FieldAccessPolicy.allowed_fields depende de la matriz de permisos (14, #5)'
        )
