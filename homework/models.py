import uuid
from django.db import models
from django.conf import settings


class Homework(models.Model):
    STATUS_CHOICES = [
        ('assigned', 'Verilib'),
        ('submitted', 'Təhvil verilib'),
        ('graded', 'Qiymətləndirilib'),
        ('overdue', 'Gecikmiş'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    lesson = models.ForeignKey('schedule.Lesson', on_delete=models.CASCADE, related_name='homeworks', verbose_name='Dərs')
    group = models.ForeignKey('courses.Group', on_delete=models.CASCADE, related_name='homeworks', verbose_name='Qrup')
    teacher = models.ForeignKey('teachers.Teacher', on_delete=models.CASCADE, related_name='assigned_homeworks', verbose_name='Müəllim')
    title = models.CharField('Başlıq', max_length=200)
    description = models.TextField('Təsvir')
    attachments = models.JSONField('Əlavələr', default=list, blank=True)
    due_date = models.DateTimeField('Son təhvil tarixi')
    max_score = models.IntegerField('Maksimum bal', default=100)
    is_active = models.BooleanField('Aktiv', default=True)
    created_at = models.DateTimeField('Yaradılma tarixi', auto_now_add=True)
    updated_at = models.DateTimeField('Yenilənmə tarixi', auto_now=True)

    class Meta:
        ordering = ('-created_at',)
        verbose_name = 'Ev tapşırığı'
        verbose_name_plural = 'Ev tapşırıqları'

    def __str__(self):
        return f"{self.title} - {self.group}"


class HomeworkSubmission(models.Model):
    STATUS_CHOICES = [
        ('submitted', 'Təhvil verilib'),
        ('graded', 'Qiymətləndirilib'),
        ('resubmitted', 'Yenidən təhvil'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    homework = models.ForeignKey(Homework, on_delete=models.CASCADE, related_name='submissions', verbose_name='Ev tapşırığı')
    student = models.ForeignKey('students.Student', on_delete=models.CASCADE, related_name='homework_submissions', verbose_name='Tələbə')
    content = models.TextField('Cavab', blank=True)
    attachments = models.JSONField('Əlavələr', default=list, blank=True)
    submitted_at = models.DateTimeField('Təhvil tarixi', auto_now_add=True)
    status = models.CharField('Status', max_length=20, choices=STATUS_CHOICES, default='submitted')
    score = models.IntegerField('Bal', null=True, blank=True)
    feedback = models.TextField('Rəy', blank=True)
    graded_by = models.ForeignKey('teachers.Teacher', on_delete=models.SET_NULL, null=True, blank=True, related_name='graded_submissions', verbose_name='Qiymətləndirən')
    graded_at = models.DateTimeField('Qiymətləndirmə tarixi', null=True, blank=True)

    class Meta:
        unique_together = ('homework', 'student')
        ordering = ('-submitted_at',)
        verbose_name = 'Tapşırıq təhvili'
        verbose_name_plural = 'Tapşırıq təhvilləri'

    def __str__(self):
        return f"{self.student} - {self.homework.title}"
