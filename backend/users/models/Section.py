# external libraries imports
from django.db import models


# main class
# what the business also calls a "process"; independent from Division, as in the specification
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
