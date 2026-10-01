# external libraries imports
from django.db import models


# main class
class OccupationalRiskInsurer(models.TextChoices):
    SURA = 'sura', 'SURA'
    SEGUROS_BOLIVAR = 'seguros_bolivar', 'SEGUROS BOLIVAR'
