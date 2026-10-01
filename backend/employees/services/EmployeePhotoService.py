# external libraries imports
import io
import mimetypes
from pathlib import PurePosixPath
from typing import TYPE_CHECKING

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.files.uploadedfile import UploadedFile
from django.http import FileResponse, Http404
from PIL import Image, ImageOps

# internal application code imports
# type hints only: importing Employee at runtime would be circular
if TYPE_CHECKING:
    from employees.models import Employee


# main class
class EmployeePhotoService:
    FORMAT_EXTENSIONS = {'JPEG': '.jpg', 'PNG': '.png', 'WEBP': '.webp'}
    THUMBNAIL_SIZE = (80, 100)

    # the previous file stays on disk on purpose: the employee's history still points to it
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
        response['Cache-Control'] = 'private, max-age=86400'

        return response

    @staticmethod
    def thumbnail_name(storage_name: str) -> str:
        path = PurePosixPath(storage_name)
        return str(path.with_name(f'{path.stem}.thumb.jpg'))

    @staticmethod
    def thumbnail_response(storage_name: str) -> FileResponse:
        if not storage_name or not default_storage.exists(storage_name):
            raise Http404

        thumbnail = EmployeePhotoService.thumbnail_name(storage_name)

        if not default_storage.exists(thumbnail):
            EmployeePhotoService._create_thumbnail(storage_name, thumbnail)

        return EmployeePhotoService.response(thumbnail)

    @staticmethod
    def _create_thumbnail(source: str, target: str) -> None:
        with default_storage.open(source, 'rb') as file:
            image = ImageOps.exif_transpose(Image.open(file)).convert('RGB')

        buffer = io.BytesIO()
        ImageOps.fit(image, EmployeePhotoService.THUMBNAIL_SIZE).save(buffer, 'JPEG', quality=85)
        saved = default_storage.save(target, ContentFile(buffer.getvalue()))

        # two requests racing to build the same thumbnail: the loser got a suffixed name
        if saved != target:
            default_storage.delete(saved)
