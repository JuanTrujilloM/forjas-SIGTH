# external libraries imports
from django.db import models


# main class
class EmployeeStatus(models.TextChoices):
    ACTIVE = 'active', 'Activo'
    RETIRED = 'retired', 'Retirado'
