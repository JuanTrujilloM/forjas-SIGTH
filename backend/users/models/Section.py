# external libraries imports
from django.db import models


# main class
# What the business also calls a "process". It does not hang from a division: the
# specification keeps division and section as two independent employee fields (5.1).
class Section(models.Model):
    # fields
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=120, unique=True, verbose_name='Nombre')
    is_active = models.BooleanField(default=True, verbose_name='Activa')

    # timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Sección'
        verbose_name_plural = 'Secciones'

    def __str__(self):
        return self.name
