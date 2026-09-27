# external libraries imports
from django.db import models


# main class
class BloodType(models.TextChoices):
    A_POSITIVE = 'a_positive', 'A+'
    A_NEGATIVE = 'a_negative', 'A-'
    B_POSITIVE = 'b_positive', 'B+'
    B_NEGATIVE = 'b_negative', 'B-'
    AB_POSITIVE = 'ab_positive', 'AB+'
    AB_NEGATIVE = 'ab_negative', 'AB-'
    O_POSITIVE = 'o_positive', 'O+'
    O_NEGATIVE = 'o_negative', 'O-'
