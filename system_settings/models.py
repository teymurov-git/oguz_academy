import uuid
from django.db import models


class SystemSetting(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    key = models.CharField('Açar', max_length=200, unique=True)
    value = models.JSONField('Dəyər')
    description = models.TextField('Təsvir', blank=True)
    is_public = models.BooleanField('Açıq', default=False)
    created_at = models.DateTimeField('Yaradılma tarixi', auto_now_add=True)
    updated_at = models.DateTimeField('Yenilənmə tarixi', auto_now=True)

    class Meta:
        ordering = ('key',)
        verbose_name = 'Sistem parametri'
        verbose_name_plural = 'Sistem parametrləri'

    def __str__(self):
        return self.key
