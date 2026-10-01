# initial catalog from the specification, kept here so the migration always replays the same data

from django.db import migrations

DIVISIONS = [
    'Dir. Administrativa, Financiera y TI',
    'Dir. Manufactura y Planeación',
    'Dir. Mercadeo y Ventas',
    'Dir. Operaciones',
    'Dir. Procesos Técnicos',
]

SECTIONS = [
    'Almacenes',
    'Cadena de Abastecimiento',
    'Cadenas',
    'Calidad',
    'Comercial',
    'Corte',
    'Despachos y Empaque',
    'Ensamble',
    'Ensamble - Proyectos',
    'Esmeriles',
    'Financiera',
    'Forja',
    'Gerencia',
    'Ingeniería',
    'Junta Directiva',
    'Logística',
    'Logística Interna',
    'Mantenimiento',
    'Manufactura',
    'Marcas',
    'Mecanizado y CDM',
    'Ordenes de Producción',
    'Oxicorte',
    'Pintura',
    'Planta de Tratamiento Térmico',
    'Procesos Técnicos',
    'Programación de Producción',
    'Servicios Externos',
    'SGI',
    'Soldadura',
    'SST',
    'Talento Humano',
    'Taller',
    'Tecnología',
    'Temple',
]


def seed(apps, schema_editor):
    Division = apps.get_model('users', 'Division')
    Section = apps.get_model('users', 'Section')

    for name in DIVISIONS:
        Division.objects.get_or_create(name=name)

    for name in SECTIONS:
        Section.objects.get_or_create(name=name)


def unseed(apps, schema_editor):
    apps.get_model('users', 'Division').objects.filter(name__in=DIVISIONS).delete()
    apps.get_model('users', 'Section').objects.filter(name__in=SECTIONS).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_access_profile_and_sections'),
    ]

    operations = [
        migrations.RunPython(seed, unseed),
    ]
