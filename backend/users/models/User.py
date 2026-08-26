# external libraries imports
from django.contrib.auth.models import AbstractUser
from django.db import models

# internal application code imports
from .Department import Department


# main class
# system user; the Department it belongs to decides which fields it may read (6.2)
class User(AbstractUser):
    # fields
    id = models.AutoField(primary_key=True)

    # relations
    department = models.ForeignKey(
        Department,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='users',
        verbose_name='Departamento',
        help_text='Vacío solo para cuentas de TI que no pertenecen a un departamento',
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
