# external libraries imports
from django.db import models
from simple_history.models import HistoricalRecords

# internal application code imports
from .Section import Section


# main class
# Explicit through table instead of Django's implicit one: every row grants access to
# people's data, so it needs timestamps, history and PROTECT (5.1)
class UserSection(models.Model):
    # fields
    id = models.AutoField(primary_key=True)

    # relations
    user = models.ForeignKey(
        'users.User',
        on_delete=models.PROTECT,
        related_name='section_assignments',
        verbose_name='Usuario',
    )
    section = models.ForeignKey(
        Section,
        on_delete=models.PROTECT,
        related_name='user_assignments',
        verbose_name='Sección',
    )

    # timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    history = HistoricalRecords()

    class Meta:
        ordering = ['user', 'section']
        verbose_name = 'Sección a cargo'
        verbose_name_plural = 'Secciones a cargo'
        constraints = [
            models.UniqueConstraint(fields=['user', 'section'], name='users_usersection_unique'),
        ]

    def __str__(self):
        return f'{self.user} · {self.section}'
