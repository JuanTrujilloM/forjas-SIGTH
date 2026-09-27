# external libraries imports
from django.db import models


# main class
class EmployeeCategory(models.TextChoices):
    ADMINISTRATIVE = 'administrative', 'Administrativos'
    PRODUCTION_APPRENTICE = 'production_apprentice', 'AprProd'
    PRODUCTION_APPRENTICE_AD = 'production_apprentice_ad', 'AprProd-Ad'
    COMMERCIAL = 'commercial', 'Comerciales'
    OPERATIVE_SUPPLY = 'operative_supply', 'Operativo-Abastecimiento'
    OPERATIVE_ADMINISTRATIVE = 'operative_administrative', 'Operativo-Administrativos'
    OPERATIVE_MANUFACTURING = 'operative_manufacturing', 'Operativo-Manufactura'
    OPERATIVE_TECHNICAL = 'operative_technical', 'Operativo-Procesos Técnicos'
