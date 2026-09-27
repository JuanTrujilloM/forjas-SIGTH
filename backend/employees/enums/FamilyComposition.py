# external libraries imports
from django.db import models


# main class
class FamilyComposition(models.TextChoices):
    LIVES_ALONE = 'lives_alone', 'Vive solo'
    WITH_PARTNER = 'with_partner', 'Vive con pareja'
    WITH_CHILDREN = 'with_children', 'Vive con hijos'
    WITH_PARENTS = 'with_parents', 'Vive con padres'
    WITH_OTHER_RELATIVES = 'with_other_relatives', 'Vive con otros familiares'
    WITH_NON_RELATIVES = 'with_non_relatives', 'Vive con personas no familiares'
    OTHER = 'other', 'Otro'
