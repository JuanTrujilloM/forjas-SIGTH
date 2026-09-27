# external libraries imports
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from simple_history.models import HistoricalRecords

# internal application code imports
from users.enums import AccessProfile
from users.managers.UserManager import UserManager
from users.validators import CorporateEmailValidator

from .Division import Division
from .Section import Section


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
    profile = models.CharField(
        max_length=30,
        choices=AccessProfile.choices,
        blank=True,
        default='',
        verbose_name='Perfil',
        help_text='Decide qué empleados y qué datos ve. Vacío solo para cuentas de TI',
    )

    # relations
    division = models.ForeignKey(
        Division,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='users',
        verbose_name='Dirección',
        help_text='Obligatoria para el perfil Director',
    )
    sections = models.ManyToManyField(
        Section,
        through='UserSection',
        blank=True,
        related_name='users',
        verbose_name='Secciones a cargo',
    )

    # timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    history = HistoricalRecords(excluded_fields=['password', 'last_login'])

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        ordering = ['email']
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

    def __str__(self):
        return self.get_full_name() or self.email

    def save(self, *args, **kwargs):
        # last_login is left out of the history, so a login alone must not add a record
        if set(kwargs.get('update_fields') or ()) == {'last_login'}:
            self.skip_history_when_saving = True

            try:
                return super().save(*args, **kwargs)
            finally:
                del self.skip_history_when_saving

        return super().save(*args, **kwargs)

    def clean(self):
        super().clean()

        if self.profile == AccessProfile.DIRECTOR and self.division_id is None:
            raise ValidationError({'division': 'Un director debe tener una dirección.'})
