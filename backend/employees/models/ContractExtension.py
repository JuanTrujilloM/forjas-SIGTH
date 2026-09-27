# external libraries imports
from django.db import models
from simple_history.models import HistoricalRecords


# main class
class ContractExtension(models.Model):
    # fields
    id = models.AutoField(primary_key=True)
    extension_date = models.DateField(verbose_name='Fecha de prórroga')

    # relations
    employee = models.ForeignKey(
        'employees.Employee',
        on_delete=models.PROTECT,
        related_name='extensions',
        verbose_name='Empleado',
    )

    # timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    history = HistoricalRecords()

    class Meta:
        ordering = ['employee', 'extension_date']
        verbose_name = 'Prórroga de contrato'
        verbose_name_plural = 'Prórrogas de contrato'
        constraints = [
            models.UniqueConstraint(
                fields=['employee', 'extension_date'],
                name='employees_contractextension_unique',
            ),
        ]

    def __str__(self):
        return f'{self.employee} · {self.extension_date:%d/%m/%Y}'
