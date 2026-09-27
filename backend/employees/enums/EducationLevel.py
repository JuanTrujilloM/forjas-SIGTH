# external libraries imports
from django.db import models


# main class
class EducationLevel(models.TextChoices):
    PRIMARY_COMPLETE = 'primary_complete', 'Primaria Completa'
    PRIMARY_INCOMPLETE = 'primary_incomplete', 'Primaria Incompleta'
    HIGH_SCHOOL_COMPLETE = 'high_school_complete', 'Bachillerato Completo'
    HIGH_SCHOOL_INCOMPLETE = 'high_school_incomplete', 'Bachillerato Incompleto'
    TECHNICAL_COMPLETE = 'technical_complete', 'Técnico Completo'
    TECHNOLOGIST_COMPLETE = 'technologist_complete', 'Tecnológico Completo'
    TECHNICAL_INCOMPLETE = 'technical_incomplete', 'Técnico / Tecnológico Incompleto'
    PROFESSIONAL_COMPLETE = 'professional_complete', 'Profesional Completo'
    PROFESSIONAL_INCOMPLETE = 'professional_incomplete', 'Profesional Incompleto'
    POSTGRADUATE = 'postgraduate', 'Especialización / Postgrado'
    MASTERS = 'masters', 'Maestría'
