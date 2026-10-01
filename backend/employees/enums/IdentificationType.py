# external libraries imports
from django.db import models


# main class
class IdentificationType(models.TextChoices):
    TI = 'ti', 'T.I.'
    CC = 'cc', 'CC'
    PPT = 'ppt', 'PPT'
    CE = 'ce', 'CE'
