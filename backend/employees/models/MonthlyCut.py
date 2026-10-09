# external libraries imports
from django.conf import settings
from django.db import models


# main class
class MonthlyCut(models.Model):
    # fields
    id = models.AutoField(primary_key=True)
    cut_date = models.DateField(
        unique=True,
        verbose_name='Fecha de corte',
        help_text='Último día del mes que conserva',
    )

    # relations
    taken_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='monthly_cuts',
        verbose_name='Tomado por',
        help_text='Vacío cuando lo tomó la tarea programada',
    )

    # timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Tomado')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Última vez rehecho')

    class Meta:
        ordering = ['-cut_date']
        verbose_name = 'Corte mensual'
        verbose_name_plural = 'Cortes mensuales'

    def __str__(self):
        return f'Corte al {self.cut_date:%d/%m/%Y}'
