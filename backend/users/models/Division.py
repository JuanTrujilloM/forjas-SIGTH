# external libraries imports
from django.db import models


# main class
class Division(models.Model):
    # fields
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=120, unique=True, verbose_name='Nombre')
    is_active = models.BooleanField(default=True, verbose_name='Activa')

    # timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Dirección'
        verbose_name_plural = 'Direcciones'

    def __str__(self):
        return self.name
