import uuid
from django.db import models


class Attendance(models.Model):
    STATUS_CHOICES = [
        ('present', 'Gəlib'),
        ('absent', 'Gəlməyib'),
        ('late', 'Gecikib'),
        ('excused', 'Üzrlü'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey('students.Student', on_delete=models.CASCADE, related_name='attendances', verbose_name='Tələbə')
    group = models.ForeignKey('courses.Group', on_delete=models.CASCADE, related_name='attendances', verbose_name='Qrup')
    lesson_date = models.DateField('Dərs tarixi', null=True, blank=True)
    lesson_number = models.IntegerField('Dərs nömrəsi', null=True, blank=True)
    status = models.CharField('Status', max_length=20, choices=STATUS_CHOICES, default='present')
    late_minutes = models.IntegerField('Gecikmə (dəq)', default=0)
    reason = models.TextField('Səbəb', blank=True)
    marked_by = models.ForeignKey('account.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='marked_attendances', verbose_name='Qeyd edən')
    created_at = models.DateTimeField('Yaradılma tarixi', auto_now_add=True)
    updated_at = models.DateTimeField('Yenilənmə tarixi', auto_now=True)

    class Meta:
        ordering = ('-lesson_date',)
        verbose_name = 'Davamiyyət'
        verbose_name_plural = 'Davamiyyətlər'
        unique_together = ('student', 'group', 'lesson_date')

    def __str__(self):
        return f"{self.student} - {self.lesson_date}"
