# external libraries imports
from rest_framework import serializers

# internal application code imports
from employees.models import Employee


# main class
class EmployeePhotoSerializer(serializers.Serializer):
    photo = serializers.ImageField(validators=Employee._meta.get_field('photo').validators)
