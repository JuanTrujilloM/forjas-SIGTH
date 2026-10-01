# the login attempt counters live in the database cache, and its table is not a model

from django.core.management import call_command
from django.db import migrations


def create_cache_table(apps, schema_editor):
    call_command('createcachetable', database=schema_editor.connection.alias)


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_seed_divisions_and_sections'),
    ]

    operations = [
        migrations.RunPython(create_cache_table, migrations.RunPython.noop),
    ]
