# external libraries imports
from django.db import models


# main class
class MaritalStatus(models.TextChoices):
    SINGLE = 'single', 'Soltero'
    MARRIED = 'married', 'Casado'
    COMMON_LAW = 'common_law', 'Unión libre'
    SEPARATED = 'separated', 'Separado/divorciado'
    WIDOWED = 'widowed', 'Viudo'
