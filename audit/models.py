import uuid
from django.db import models
from django.conf import settings


class AuditLog(models.Model):
    ACTION_CHOICES = [
        ('create', 'Yaratma'),
        ('update', 'Yeniləmə'),
        ('delete', 'Silinmə'),
        ('login', 'Giriş'),
        ('logout', 'Çıxış'),
        ('export', 'İxrac'),
        ('import', 'İmport'),
        ('view', 'Baxış'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='audit_logs', verbose_name='İstifadəçi')
    action = models.CharField('Əməliyyat', max_length=20, choices=ACTION_CHOICES)
    module = models.CharField('Modul', max_length=100)
    model_name = models.CharField('Model', max_length=100, blank=True)
    object_id = models.CharField('Obyekt ID', max_length=100, blank=True)
    object_repr = models.CharField('Obyekt', max_length=300, blank=True)
    details = models.JSONField('Detallar', default=dict, blank=True)
    ip_address = models.GenericIPAddressField('IP ünvanı', blank=True, null=True)
    user_agent = models.TextField('Brauzer', blank=True)
    is_system = models.BooleanField('Sistem', default=False)
    created_at = models.DateTimeField('Tarix', auto_now_add=True)

    class Meta:
        ordering = ('-created_at',)
        verbose_name = 'Audit jurnalı'
        verbose_name_plural = 'Audit jurnalı'

    def __str__(self):
        return f"{self.user} - {self.action} - {self.module}"
