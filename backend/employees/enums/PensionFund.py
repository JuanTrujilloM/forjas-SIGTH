# external libraries imports
from django.db import models


# main class
class PensionFund(models.TextChoices):
    COLFONDOS = 'colfondos', 'Colfondos'
    COLPENSIONES = 'colpensiones', 'Colpensiones'
    SKANDIA = 'skandia', 'Old Mutual - Skandia'
    PENSIONER = 'pensioner', 'Pensionado'
    PORVENIR = 'porvenir', 'Porvenir'
    PROTECCION = 'proteccion', 'Protección'
