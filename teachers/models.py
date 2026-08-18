import uuid
from django.db import models
from django.conf import settings


class Teacher(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='teacher_profile', verbose_name='İstifadəçi')
    teacher_id = models.CharField('Müəllim ID', max_length=50, unique=True, blank=True)
    employee = models.ForeignKey('employees.Employee', on_delete=models.SET_NULL, null=True, blank=True, related_name='teacher_profile', verbose_name='İşçi')
    patronymic = models.CharField('Ata adı', max_length=150, blank=True)
    date_of_birth = models.DateField('Doğum tarixi', null=True, blank=True)
    specialization = models.CharField('İxtisas', max_length=200, blank=True)
    bio = models.TextField('Bioqrafiya', blank=True)
    education = models.JSONField('Təhsil', default=list, blank=True)
    certificates = models.JSONField('Sertifikatlar', default=list, blank=True)
    subjects = models.JSONField('Fənlər', default=list, blank=True)
    hourly_rate = models.DecimalField('Saatlıq tarif', max_digits=10, decimal_places=2, default=0)
    phone = models.CharField('Telefon', max_length=50, blank=True)
    is_active = models.BooleanField('Aktiv', default=True)
    academic_year = models.ForeignKey('courses.AcademicYear', on_delete=models.SET_NULL, null=True, blank=True, related_name='teachers', verbose_name='Tədris ili')
    created_at = models.DateTimeField('Yaradılma tarixi', auto_now_add=True)
    updated_at = models.DateTimeField('Yenilənmə tarixi', auto_now=True)

    class Meta:
        ordering = ('-created_at',)
        verbose_name = 'Müəllim'
        verbose_name_plural = 'Müəllimlər'

    def save(self, *args, **kwargs):
        if not self.teacher_id:
            self.teacher_id = f"TCH-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.user.get_full_name() or self.user.username
