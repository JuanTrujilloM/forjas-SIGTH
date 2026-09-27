# external libraries imports
from django.db import models


# main class
class Position(models.Model):
    # fields
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=150, unique=True, verbose_name='Nombre')
    is_active = models.BooleanField(default=True, verbose_name='Activo')

    # timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Cargo'
        verbose_name_plural = 'Cargos'

    def __str__(self):
        return self.name
