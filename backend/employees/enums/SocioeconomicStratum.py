# external libraries imports
from django.db import models


# main class
class SocioeconomicStratum(models.IntegerChoices):
    STRATUM_1 = 1, '1'
    STRATUM_2 = 2, '2'
    STRATUM_3 = 3, '3'
    STRATUM_4 = 4, '4'
    STRATUM_5 = 5, '5'
    STRATUM_6 = 6, '6'
