# external libraries imports
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    # RenameModel and RenameField, not Delete + Create: they rename the table and the
    # column in place, so the rows already loaded survive the rename. Regenerating this
    # file with makemigrations produces the destructive variant, because the autodetector
    # only proposes a rename interactively.
    operations = [
        migrations.RenameModel(
            old_name='Department',
            new_name='Division',
        ),
        migrations.RenameField(
            model_name='user',
            old_name='department',
            new_name='division',
        ),
        migrations.AlterModelOptions(
            name='division',
            options={
                'ordering': ['name'],
                'verbose_name': 'Dirección',
                'verbose_name_plural': 'Direcciones',
            },
        ),
        migrations.AlterField(
            model_name='user',
            name='division',
            field=models.ForeignKey(
                blank=True,
                help_text='Vacío solo para cuentas de TI que no pertenecen a una dirección',
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='users',
                to='users.division',
                verbose_name='Dirección',
            ),
        ),
        migrations.AddField(
            model_name='division',
            name='has_full_employee_access',
            field=models.BooleanField(
                default=False,
                help_text='Solo para Talento Humano: ignora el alcance por dirección (6.1)',
                verbose_name='Ve todos los empleados',
            ),
        ),
    ]
