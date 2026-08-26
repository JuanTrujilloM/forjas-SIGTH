# external libraries imports
from django.db import models


# main class
# company department; its code is the key of the field access matrix (6.2)
class Department(models.Model):
    # fields
    id = models.AutoField(primary_key=True)
    code = models.CharField(max_length=20, unique=True, verbose_name='Código')
    name = models.CharField(max_length=120, verbose_name='Nombre')
    is_active = models.BooleanField(default=True, verbose_name='Activo')

    # timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Departamento'
        verbose_name_plural = 'Departamentos'

    def __str__(self):
        return self.name
