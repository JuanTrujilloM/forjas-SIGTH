# external libraries imports
from django.db import models


# main class
class Ethnicity(models.TextChoices):
    INDIGENOUS = 'indigenous', 'Indígena'
    ROMA = 'roma', 'Gitano(a) / Rrom'
    RAIZAL = 'raizal', 'Raizal del Archipiélago de San Andrés, Providencia y Santa Catalina'
    PALENQUERO = 'palenquero', 'Palenquero(a) de San Basilio'
    AFRO_COLOMBIAN = 'afro_colombian', 'Negro(a), mulato(a), afrodescendiente o afrocolombiano(a)'
    NONE = 'none', 'Ningún grupo étnico'
    UNDISCLOSED = 'undisclosed', 'No informa / Prefiere no responder'
