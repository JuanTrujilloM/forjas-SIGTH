# external libraries imports
from pathlib import Path

from django.urls import reverse
from rest_framework import serializers

# internal application code imports
from employees.models import Employee


# main class
# the photo endpoint keeps the row scope; the file name in the url invalidates the cache
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
