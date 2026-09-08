# external libraries imports
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible


# main class
@deconstructible(path='users.validators.CorporateEmailValidator')
class CorporateEmailValidator:
    def __call__(self, value: str) -> None:
        domain = settings.CORPORATE_EMAIL_DOMAIN

        if not value or not value.lower().endswith(f'@{domain.lower()}'):
            raise ValidationError(
                f'El correo debe pertenecer al dominio corporativo @{domain}.',
                code='non_corporate_email',
            )

    def __eq__(self, other: object) -> bool:
        return isinstance(other, CorporateEmailValidator)
