# external libraries imports
from django.db import models


# main class
class SeveranceFund(models.TextChoices):
    COLFONDOS = 'colfondos', 'Colfondos'
    SKANDIA = 'skandia', 'Old Mutual - Skandia'
    PORVENIR = 'porvenir', 'Porvenir'
    PROTECCION = 'proteccion', 'Protección'
