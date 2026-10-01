# external libraries imports
from pathlib import Path
from uuid import uuid4

from django.db.models import Model
from django.utils.deconstruct import deconstructible


# main class
# A random name instead of the uploaded one, which often carries the person's name
@deconstructible(path='employees.services.EmployeePhotoPath')
class EmployeePhotoPath:
    def __call__(self, instance: Model, filename: str) -> str:
        return f'employees/photos/{uuid4().hex}{Path(filename).suffix.lower()}'

    def __eq__(self, other: object) -> bool:
        return isinstance(other, EmployeePhotoPath)
