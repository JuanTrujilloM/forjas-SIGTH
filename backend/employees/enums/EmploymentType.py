# external libraries imports
from django.db import models


# main class
class EmploymentType(models.TextChoices):
    DIRECT = 'direct', 'Directa'
    TEMPORARY_AD = 'temporary_ad', 'Temporal-Ad'
    TEMPORARY_SAI = 'temporary_sai', 'Temporal-Sai'
