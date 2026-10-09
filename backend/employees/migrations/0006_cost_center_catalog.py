# the cost center becomes a catalog: the code stays, the name is filled in by Talent Management

import django.db.models.deletion
from django.db import migrations, models

# the specification only lists the codes; the code doubles as name until the admin renames it
CODES = [
    'PCOFB20000',
    'PCOFB20114',
    'PCOFB20300',
    'PCOFB30200',
    'PCOFB30201',
    'PCOFB30202',
    'PCOFB30203',
    'PCOFB30205',
    'PCOFB30206',
    'PCOFB30207',
    'PCOFB30208',
    'PCOFB30209',
    'PCOFB30300',
    'PCOFB30500',
    'PCOFB30503',
    'PCOFB30601',
    'PCOFB40100',
    'PCOFB40400',
    'PCOFB50103',
    'PCOFB50302',
    'PCOFB50400',
]


def seed(apps, schema_editor):
    CostCenter = apps.get_model('employees', 'CostCenter')

    for code in CODES:
        CostCenter.objects.get_or_create(code=code, defaults={'name': code})


def unseed(apps, schema_editor):
    apps.get_model('employees', 'CostCenter').objects.filter(code__in=CODES).delete()


# the history keeps the code too, so past versions still point to the right catalog row
def codes_to_catalog(apps, schema_editor):
    ids_by_code = dict(apps.get_model('employees', 'CostCenter').objects.values_list('code', 'id'))

    for model_name in ['Employee', 'HistoricalEmployee']:
        model = apps.get_model('employees', model_name)

        for code, catalog_id in ids_by_code.items():
            model.objects.filter(cost_center=code).update(cost_center_ref_id=catalog_id)


def catalog_to_codes(apps, schema_editor):
    codes_by_id = dict(apps.get_model('employees', 'CostCenter').objects.values_list('id', 'code'))

    for model_name in ['Employee', 'HistoricalEmployee']:
        model = apps.get_model('employees', model_name)

        for catalog_id, code in codes_by_id.items():
            model.objects.filter(cost_center_ref_id=catalog_id).update(cost_center=code)


class Migration(migrations.Migration):

    dependencies = [
        ('employees', '0005_require_employee_fields_and_add_training'),
    ]

    operations = [
        migrations.CreateModel(
            name='CostCenter',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('code', models.CharField(max_length=20, unique=True, verbose_name='Código')),
                ('name', models.CharField(max_length=150, verbose_name='Nombre')),
                ('is_active', models.BooleanField(default=True, verbose_name='Activo')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Centro de costos',
                'verbose_name_plural': 'Centros de costos',
                'ordering': ['code'],
            },
        ),
        migrations.RunPython(seed, unseed),
        migrations.AddField(
            model_name='employee',
            name='cost_center_ref',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='employees', to='employees.costcenter', verbose_name='Centro de costos'),
        ),
        migrations.AddField(
            model_name='historicalemployee',
            name='cost_center_ref',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='employees.costcenter', verbose_name='Centro de costos'),
        ),
        migrations.RunPython(codes_to_catalog, catalog_to_codes),
        migrations.RemoveField(
            model_name='employee',
            name='cost_center',
        ),
        migrations.RemoveField(
            model_name='historicalemployee',
            name='cost_center',
        ),
        migrations.RenameField(
            model_name='employee',
            old_name='cost_center_ref',
            new_name='cost_center',
        ),
        migrations.RenameField(
            model_name='historicalemployee',
            old_name='cost_center_ref',
            new_name='cost_center',
        ),
        migrations.AlterField(
            model_name='employee',
            name='cost_center',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='employees', to='employees.costcenter', verbose_name='Centro de costos'),
        ),
    ]
