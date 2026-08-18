import uuid
from django.db import models
from django.conf import settings


def file_upload_path(instance, filename):
    return f"uploads/{instance.module}/{instance.folder_id}/{filename}"


class File(models.Model):
    MODULE_CHOICES = [
        ('students', 'Tələbələr'),
        ('teachers', 'Müəllimlər'),
        ('employees', 'İşçilər'),
        ('courses', 'Kurslar'),
        ('finance', 'Maliyyə'),
        ('general', 'Ümumi'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    file = models.FileField('Fayl', upload_to=file_upload_path)
    original_filename = models.CharField('Orijinal ad', max_length=500)
    file_size = models.BigIntegerField('Ölçü (bayt)', default=0)
    mime_type = models.CharField('MIME tipi', max_length=200, blank=True)
    module = models.CharField('Modul', max_length=50, choices=MODULE_CHOICES, default='general')
    folder_id = models.CharField('Qovluq ID', max_length=100, blank=True)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='uploaded_files', verbose_name='Yükləyən')
    description = models.TextField('Təsvir', blank=True)
    is_active = models.BooleanField('Aktiv', default=True)
    created_at = models.DateTimeField('Yaradılma tarixi', auto_now_add=True)

    class Meta:
        ordering = ('-created_at',)
        verbose_name = 'Fayl'
        verbose_name_plural = 'Fayllar'

    def __str__(self):
        return self.original_filename
