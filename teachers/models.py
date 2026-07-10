from django.db import models
from django.conf import settings


class Teacher(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='teacher_profile')
    phone = models.CharField('phone', max_length=50)
    specialization = models.CharField('specialization', max_length=200)
    bio = models.TextField('bio', blank=True)
    hire_date = models.DateField('hire date', auto_now_add=True)
    is_active = models.BooleanField('active', default=True)

    class Meta:
        verbose_name = 'Teacher'
        verbose_name_plural = 'Teachers'

    def __str__(self):
        return self.user.get_full_name() or self.user.username
