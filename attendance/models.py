from django.db import models


class Attendance(models.Model):
    STATUS_CHOICES = [
        ('present', 'Gəldi'),
        ('absent', 'Gəlmədi'),
        ('late', 'Gecikdi'),
    ]

    group = models.ForeignKey('courses.Group', on_delete=models.CASCADE, related_name='attendances')
    student = models.ForeignKey('students.Student', on_delete=models.CASCADE, related_name='attendances')
    date = models.DateField('date')
    status = models.CharField('status', max_length=20, choices=STATUS_CHOICES, default='present')
    note = models.TextField('note', blank=True)

    class Meta:
        verbose_name = 'Attendance'
        verbose_name_plural = 'Attendances'
        unique_together = ('group', 'student', 'date')

    def __str__(self):
        return f"{self.student} - {self.date} - {self.get_status_display()}"
