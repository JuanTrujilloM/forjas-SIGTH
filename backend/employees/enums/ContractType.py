# external libraries imports
from django.db import models


# main class
class ContractType(models.TextChoices):
    FIXED_THREE_MONTHS = 'fixed_three_months', 'Fijo 3 meses'
    FIXED_SIX_MONTHS = 'fixed_six_months', 'Fijo 6 meses'
    FIXED_SPECIAL = 'fixed_special', 'Fijo Especial'
    FIXED_ONE_YEAR = 'fixed_one_year', 'Fijo un año'
    INDEFINITE = 'indefinite', 'Indefinido'
    WORK_AND_LABOR = 'work_and_labor', 'Obra y Labor'
