# external libraries imports
from django.db import models


# main class
class SalaryType(models.TextChoices):
    BASIC = 'basic', 'Básico'
    APPRENTICE_SUPPORT = 'apprentice_support', 'Apoyo Sostenimiento'
    INTEGRAL = 'integral', 'Integral'
