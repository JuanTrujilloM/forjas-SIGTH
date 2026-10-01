# external libraries imports
from django.db import models


# main class
class HealthInsurer(models.TextChoices):
    ADRES = 'adres', 'Adres - Fosyga'
    COOSALUD = 'coosalud', 'Coosalud'
    COMPENSAR = 'compensar', 'Compensar'
    NUEVA_EPS = 'nueva_eps', 'Nueva EPS'
    SALUD_TOTAL = 'salud_total', 'Salud Total EPS'
    SANITAS = 'sanitas', 'Sanitas'
    SAVIA_SALUD = 'savia_salud', 'Savia Salud EPS'
    SURA = 'sura', 'Sura EPS'
