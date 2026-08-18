import uuid
from django.db import models
from django.conf import settings


class Notification(models.Model):
    TYPE_CHOICES = [
        ('info', 'Məlumat'),
        ('warning', 'Xəbərdarlıq'),
        ('success', 'Uğurlu'),
        ('error', 'Xəta'),
        ('payment', 'Ödəniş'),
        ('attendance', 'Davam'),
        ('homework', 'Ev tapşırığı'),
        ('schedule', 'Cədvəl'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications', verbose_name='Alıcı')
    notification_type = models.CharField('Növ', max_length=20, choices=TYPE_CHOICES, default='info')
    title = models.CharField('Başlıq', max_length=200)
    message = models.TextField('Mesaj')
    icon = models.CharField('İkon', max_length=50, blank=True)
    link = models.CharField('Link', max_length=500, blank=True)
    is_read = models.BooleanField('Oxunub', default=False)
    is_system = models.BooleanField('Sistem', default=False)
    created_at = models.DateTimeField('Yaradılma tarixi', auto_now_add=True)

    class Meta:
        ordering = ('-created_at',)
        verbose_name = 'Bildiriş'
        verbose_name_plural = 'Bildirişlər'

    def __str__(self):
        return f"{self.recipient.email} - {self.title}"


class NotificationTemplate(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    key = models.CharField(max_length=200, unique=True)
    title_template = models.CharField('Başlıq şablonu', max_length=200)
    body_template = models.TextField('Mətn şablonu')
    notification_type = models.CharField('Növ', max_length=20, choices=Notification.TYPE_CHOICES, default='info')

    class Meta:
        verbose_name = 'Bildiriş şablonu'
        verbose_name_plural = 'Bildiriş şablonları'

    def __str__(self):
        return self.key
