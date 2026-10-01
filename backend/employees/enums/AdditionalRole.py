# external libraries imports
from django.db import models


# main class
class AdditionalRole(models.TextChoices):
    NONE = 'none', 'Ninguno'
    BRIGADIER = 'brigadier', 'Brigadista'
    COEXISTENCE_COMMITTEE = 'coexistence_committee', 'Comité de Convivencia'
    COPASST = 'copasst', 'COPASST'
    FORKLIFT_OPERATOR = 'forklift_operator', 'Op. Montacargas'
