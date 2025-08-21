from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class User(AbstractUser):
    email = models.EmailField('email',unique=True)
    phone = models.CharField('phone',max_length=15, blank=True, null=True)
    photo = models.ImageField('photo',
    upload_to='profile_photos/', blank=True, null=True)

    def __str__(self):
        return self.username