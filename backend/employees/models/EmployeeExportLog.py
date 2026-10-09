# external libraries imports
from django.conf import settings
from django.db import models


# main class
class EmployeeExportLog(models.Model):
    # fields
    id = models.AutoField(primary_key=True)
    file_format = models.CharField(max_length=10, verbose_name='Formato')
    title = models.CharField(max_length=200, verbose_name='Reporte')
    filters = models.JSONField(default=dict, verbose_name='Filtros')
    fields = models.JSONField(default=list, verbose_name='Campos')
    row_count = models.PositiveIntegerField(verbose_name='Filas')

    # relations
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='employee_exports',
        verbose_name='Usuario',
    )

    # timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at', '-id']
        verbose_name = 'Descarga de empleados'
        verbose_name_plural = 'Descargas de empleados'

    def __str__(self):
        return f'{self.user} · {self.title} · {self.file_format}'
