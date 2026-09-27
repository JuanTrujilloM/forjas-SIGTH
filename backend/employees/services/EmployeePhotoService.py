# external libraries imports
import mimetypes
from typing import TYPE_CHECKING

from django.core.files.storage import default_storage
from django.core.files.uploadedfile import UploadedFile
from django.http import FileResponse, Http404

# internal application code imports
# Employee imports this package for its upload path, so importing it back at runtime
# would be circular; it is only needed for the type hints
if TYPE_CHECKING:
    from employees.models import Employee


# main class
class EmployeePhotoService:
    FORMAT_EXTENSIONS = {'JPEG': '.jpg', 'PNG': '.png', 'WEBP': '.webp'}

    # The previous file stays on disk on purpose: the employee's history still points to
    # it (5.2). Deleting it waits for the history retention rule.
    @staticmethod
    def replace(employee: 'Employee', photo: UploadedFile) -> None:
        photo.name = f'photo{EmployeePhotoService.FORMAT_EXTENSIONS[photo.image.format]}'
        employee.photo = photo
        employee.save(update_fields=['photo', 'updated_at'])

    @staticmethod
    def remove(employee: 'Employee') -> None:
        employee.photo = None
        employee.save(update_fields=['photo', 'updated_at'])

    @staticmethod
    def response(storage_name: str) -> FileResponse:
        if not storage_name or not default_storage.exists(storage_name):
            raise Http404

        content_type, _ = mimetypes.guess_type(storage_name)
        response = FileResponse(default_storage.open(storage_name, 'rb'), content_type=content_type)
        # the url carries the file's name as its version, so a cached copy never goes stale
        response['Cache-Control'] = 'private, max-age=86400'

        return response
