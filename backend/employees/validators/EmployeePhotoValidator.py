# external libraries imports
from django.core.exceptions import ValidationError
from django.core.files import File
from django.utils.deconstruct import deconstructible


# main class
@deconstructible(path='employees.validators.EmployeePhotoValidator')
class EmployeePhotoValidator:
    MAX_BYTES = 5 * 1024 * 1024
    ALLOWED_FORMATS = frozenset({'JPEG', 'PNG', 'WEBP'})

    def __call__(self, value: File) -> None:
        if value.size > self.MAX_BYTES:
            raise ValidationError('La foto no puede pesar más de 5 MB.', code='photo_too_large')

        # Only a freshly uploaded file carries the image Pillow opened; the extension alone
        # proves nothing, so SVG or HTML renamed to .jpg is rejected here
        image = getattr(value, 'image', None)

        if image is not None and image.format not in self.ALLOWED_FORMATS:
            raise ValidationError('La foto debe ser JPG, PNG o WebP.', code='photo_format')

    def __eq__(self, other: object) -> bool:
        return isinstance(other, EmployeePhotoValidator)
