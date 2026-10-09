# external libraries imports
from django.db import models

# internal application code imports
from employees.enums import EmployeeStatus


# main class
# division, section and status are real columns because the row scope and the filters use them
class EmployeeSnapshot(models.Model):
    # fields
    id = models.AutoField(primary_key=True)
    full_name = models.CharField(max_length=200, verbose_name='Apellidos y nombres')
    id_number = models.PositiveBigIntegerField(verbose_name='Identificación')
    status = models.CharField(max_length=20, choices=EmployeeStatus.choices, verbose_name='Estado')
    data = models.JSONField(
        verbose_name='Datos',
        help_text='Todas las columnas del empleado a la fecha de corte; el perfil se aplica al leer',
    )

    # relations
    cut = models.ForeignKey(
        'MonthlyCut', on_delete=models.PROTECT, related_name='snapshots', verbose_name='Corte'
    )
    employee = models.ForeignKey(
        'Employee', on_delete=models.PROTECT, related_name='snapshots', verbose_name='Empleado'
    )
    division = models.ForeignKey(
        'users.Division',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='employee_snapshots',
        verbose_name='Dirección',
    )
    section = models.ForeignKey(
        'users.Section',
        on_delete=models.PROTECT,
        related_name='employee_snapshots',
        verbose_name='Sección',
    )

    # timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['full_name', 'id']
        verbose_name = 'Empleado en un corte'
        verbose_name_plural = 'Empleados en cortes'
        constraints = [
            models.UniqueConstraint(
                fields=['cut', 'employee'], name='employees_employeesnapshot_unique'
            ),
        ]

    def __str__(self):
        return f'{self.full_name} · {self.cut}'
