import uuid
from django.db import models
from django.conf import settings


class Schedule(models.Model):
    DAY_CHOICES = [
        ('monday', 'Bazar ertəsi'),
        ('tuesday', 'Çərşənbə axşamı'),
        ('wednesday', 'Çərşənbə'),
        ('thursday', 'Cümə axşamı'),
        ('friday', 'Cümə'),
        ('saturday', 'Şənbə'),
        ('sunday', 'Bazar'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    group = models.ForeignKey('courses.Group', on_delete=models.CASCADE, related_name='schedules', verbose_name='Qrup')
    teacher = models.ForeignKey('teachers.Teacher', on_delete=models.CASCADE, related_name='schedules', verbose_name='Müəllim')
    day_of_week = models.CharField('Həftənin günü', max_length=20, choices=DAY_CHOICES)
    start_time = models.TimeField('Başlama vaxtı')
    end_time = models.TimeField('Bitmə vaxtı')
    lesson_duration = models.IntegerField('Dərs müddəti (dəq)', default=60)
    is_active = models.BooleanField('Aktiv', default=True)
    created_at = models.DateTimeField('Yaradılma tarixi', auto_now_add=True)
    updated_at = models.DateTimeField('Yenilənmə tarixi', auto_now=True)

    class Meta:
        ordering = ('day_of_week', 'start_time')
        verbose_name = 'Cədvəl'
        verbose_name_plural = 'Cədvəllər'

    def __str__(self):
        return f"{self.group.name} - {self.get_day_of_week_display()} {self.start_time}"


class Lesson(models.Model):
    STATUS_CHOICES = [
        ('scheduled', 'Planlaşdırılıb'),
        ('in_progress', 'Davam edir'),
        ('completed', 'Bitib'),
        ('cancelled', 'Ləğv olunub'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    group = models.ForeignKey('courses.Group', on_delete=models.CASCADE, related_name='lessons', verbose_name='Qrup')
    schedule = models.ForeignKey(Schedule, on_delete=models.SET_NULL, null=True, blank=True, related_name='lessons', verbose_name='Cədvəl')
    teacher = models.ForeignKey('teachers.Teacher', on_delete=models.CASCADE, related_name='lessons', verbose_name='Müəllim')
    lesson_number = models.IntegerField('Dərs nömrəsi')
    date = models.DateField('Tarix')
    start_time = models.TimeField('Başlama vaxtı')
    end_time = models.TimeField('Bitmə vaxtı')
    topic = models.CharField('Mövzu', max_length=300, blank=True)
    objectives = models.TextField('Məqsədlər', blank=True)
    materials = models.JSONField('Materiallar', default=list, blank=True)
    homework = models.TextField('Ev tapşırığı', blank=True)
    notes = models.TextField('Qeydlər', blank=True)
    video_recording = models.URLField('Video yazı', blank=True)
    status = models.CharField('Status', max_length=20, choices=STATUS_CHOICES, default='scheduled')
    created_at = models.DateTimeField('Yaradılma tarixi', auto_now_add=True)
    updated_at = models.DateTimeField('Yenilənmə tarixi', auto_now=True)

    class Meta:
        ordering = ('date', 'start_time')
        unique_together = ('group', 'lesson_number')
        verbose_name = 'Dərs'
        verbose_name_plural = 'Dərslər'

    def __str__(self):
        return f"{self.group} - Dərs {self.lesson_number}"


class LessonAttendance(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='lesson_attendances', verbose_name='Dərs')
    student = models.ForeignKey('students.Student', on_delete=models.CASCADE, related_name='lesson_attendances', verbose_name='Tələbə')
    status = models.CharField('Status', max_length=20, choices=[
        ('present', 'Gəlib'),
        ('absent', 'Gəlməyib'),
        ('late', 'Gecikib'),
        ('excused', 'Üzrlü'),
    ], default='absent')
    late_minutes = models.IntegerField('Gecikmə (dəq)', default=0)
    points = models.IntegerField('Bal', null=True, blank=True)
    note = models.TextField('Qeyd', blank=True)

    class Meta:
        unique_together = ('lesson', 'student')
        verbose_name = 'Dərs davamiyyəti'
        verbose_name_plural = 'Dərs davamiyyətləri'

    def __str__(self):
        return f"{self.student} - Dərs {self.lesson.lesson_number}"
