# external libraries imports
from django.db import models


# main class
# company division; it is the unit that scopes which employees a user may see (6.1)
class Division(models.Model):
    # fields
    id = models.AutoField(primary_key=True)
    code = models.CharField(max_length=20, unique=True, verbose_name='Código')
    name = models.CharField(max_length=120, verbose_name='Nombre')
    is_active = models.BooleanField(default=True, verbose_name='Activo')
    has_full_employee_access = models.BooleanField(
        default=False,
        verbose_name='Ve todos los empleados',
        help_text='Solo para Talento Humano: ignora el alcance por dirección (6.1)',
    )

    # timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Dirección'
        verbose_name_plural = 'Direcciones'

    def __str__(self):
        return self.name
