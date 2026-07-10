from django.db import models
from django.conf import settings


class Student(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='student_profile')
    phone = models.CharField('phone', max_length=50)
    parent_phone = models.CharField('parent phone', max_length=50, blank=True)
    address = models.TextField('address', blank=True)
    date_of_birth = models.DateField('date of birth', null=True, blank=True)
    enrollment_date = models.DateField('enrollment date', auto_now_add=True)
    is_active = models.BooleanField('active', default=True)

    class Meta:
        verbose_name = 'Student'
        verbose_name_plural = 'Students'

    def __str__(self):
        return self.user.get_full_name() or self.user.username
