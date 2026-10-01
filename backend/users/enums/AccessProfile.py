# external libraries imports
from django.db import models


# main class
class AccessProfile(models.TextChoices):
    TALENT_MANAGEMENT = 'talent_management', 'Talento Humano'
    GENERAL_MANAGEMENT = 'general_management', 'Gerencia General'
    OCCUPATIONAL_SAFETY = 'occupational_safety', 'SST - SGI'
    DIRECTOR = 'director', 'Director'
    LEADER = 'leader', 'Líder'
