# external libraries imports
from django.contrib.auth.models import AbstractUser
from django.db import models

# internal application code imports
from users.managers.UserManager import UserManager
from users.validators import CorporateEmailValidator

from .Division import Division


# main class
class User(AbstractUser):
    username = None

    # fields
    id = models.AutoField(primary_key=True)
    email = models.EmailField(
        unique=True,
        validators=[CorporateEmailValidator()],
        verbose_name='Correo corporativo',
        help_text='Es el identificador de acceso al sistema',
    )

    # relations
    division = models.ForeignKey(
        Division,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='users',
        verbose_name='Dirección',
        help_text='Vacío solo para cuentas de TI que no pertenecen a una dirección',
    )

    # timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        ordering = ['email']
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

    def __str__(self):
        return self.get_full_name() or self.email
