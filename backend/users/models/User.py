# external libraries imports
from django.contrib.auth.models import AbstractUser
from django.db import models

# internal application code imports
from .Division import Division


# main class
# system user; the Division it belongs to decides which employees it may see (6.1)
class User(AbstractUser):
    # fields
    id = models.AutoField(primary_key=True)

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

    class Meta:
        ordering = ['username']
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

    def __str__(self):
        return self.get_full_name() or self.username
