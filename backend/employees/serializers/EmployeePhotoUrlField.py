# external libraries imports
from pathlib import Path

from django.urls import reverse
from rest_framework import serializers

# internal application code imports
from employees.models import Employee


# main class
# The url points to the photo endpoint and not to MEDIA_URL, so the file goes out behind
# the same row scope as the rest of the employee (6.4). The file name is the version, so
# a cached copy never outlives a new photo.
class EmployeePhotoUrlField(serializers.Field):
    def __init__(self, thumbnail: bool = False, **kwargs):
        kwargs['source'] = '*'
        kwargs['read_only'] = True
        super().__init__(**kwargs)
        self.thumbnail = thumbnail

    def to_representation(self, employee: Employee) -> str | None:
        if not employee.photo:
            return None

        url = reverse('employees.employee-photo', args=[employee.pk])
        query = f'v={Path(employee.photo.name).stem}'

        if self.thumbnail:
            query += '&size=thumb'

        return self.context['request'].build_absolute_uri(f'{url}?{query}')
