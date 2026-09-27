# external libraries imports
from django.db import models


# main class
class EvaluationGroup(models.TextChoices):
    OPERATIVE = 'operative', 'Operativo'
    ANALYST = 'analyst', 'Analista / Auxiliar'
    COMMERCIAL = 'commercial', 'Comercial'
    LEADER = 'leader', 'Líder / Coordinador'
    DIRECTOR = 'director', 'Director'
