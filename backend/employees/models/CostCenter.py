# external libraries imports
from django.db import models


# main class
class CostCenter(models.Model):
    # fields
    id = models.AutoField(primary_key=True)
    code = models.CharField(max_length=20, unique=True, verbose_name='Código')
    name = models.CharField(max_length=150, verbose_name='Nombre')
    is_active = models.BooleanField(default=True, verbose_name='Activo')

    # timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['code']
        verbose_name = 'Centro de costos'
        verbose_name_plural = 'Centros de costos'

    def __str__(self):
        return f'{self.code} — {self.name}'
