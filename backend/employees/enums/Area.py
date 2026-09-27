# external libraries imports
from django.db import models


# main class
class Area(models.TextChoices):
    ADMON_51 = 'ADMON-51', 'ADMON-51'
    CIF_73 = 'CIF-73', 'CIF -73'
    LOG_52 = 'LOG-52', 'LOG-52'
    MOD_72 = 'MOD-72', 'MOD-72'
    VENTAS_52 = 'VENTAS-52', 'VENTAS-52'
