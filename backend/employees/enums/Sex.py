# external libraries imports
from django.db import models


# main class
class Sex(models.TextChoices):
    FEMALE = 'female', 'Femenino'
    MALE = 'male', 'Masculino'
