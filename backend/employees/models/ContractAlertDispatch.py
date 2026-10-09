# external libraries imports
from django.db import models


# main class
class ContractAlertDispatch(models.Model):
    # fields
    id = models.AutoField(primary_key=True)
    sent_on = models.DateField(
        unique=True,
        verbose_name='Fecha',
        help_text='Un registro por día: evita que el correo salga dos veces',
    )
    recipients = models.TextField(verbose_name='Destinatarios')
    employee_count = models.PositiveIntegerField(verbose_name='Empleados en alerta')

    # timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Enviado')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-sent_on']
        verbose_name = 'Envío de vencimientos'
        verbose_name_plural = 'Envíos de vencimientos'

    def __str__(self):
        return f'{self.sent_on:%d/%m/%Y} · {self.employee_count} empleados'
