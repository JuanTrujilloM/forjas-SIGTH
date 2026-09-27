# Initial catalog taken from Talent Management's field specification (5.1). It is known
# to be incomplete; Talent Management adds the missing positions from the admin.

from django.db import migrations

POSITIONS = [
    'Almacenista Producto Intermedio',
    'Analista de Compras',
    'Analista de Costos',
    'Analista Dibujante de Ingeniería',
    'Analista SGI',
    'Aprendiz',
    'Auxiliar Almacén Despachos',
    'Conductor',
    'Coordinador de Sección - Mecanizado y CDM',
    'Coordinador de Sección - Soldadura y Pintura',
    'Coordinador Oxicorte y Corte',
    'Ejecutivo Comercial',
    'Ingeniero Soporte Técnico Senior',
    'Mecánico de Banco',
    'Mecánico de Mantenimiento',
    'Mecánico de Mantenimiento - Electricista',
    'Oficial de Mantenimiento Locativo',
    'Operario auditoria de inventarios',
    'Operario Cadenas',
    'Operario CDM',
    'Operario CDM - Experto',
    'Operario CDM - Montador',
    'Operario Corte',
    'Operario Corte Láser',
    'Operario Forja Básico',
    'Operario Logística Interna - Proyectos',
    'Operario Soldador Básico (GMAW -SMAW)',
    'Operario Soldador Formación (GMAW -SMAW)',
    'Operario Torno',
    'Operario Torno y CDM',
    'Operario Tratamiento Térmico',
]


def seed(apps, schema_editor):
    Position = apps.get_model('employees', 'Position')

    for name in POSITIONS:
        Position.objects.get_or_create(name=name)


def unseed(apps, schema_editor):
    apps.get_model('employees', 'Position').objects.filter(name__in=POSITIONS).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('employees', '0001_employee_and_catalogs'),
    ]

    operations = [
        migrations.RunPython(seed, unseed),
    ]
