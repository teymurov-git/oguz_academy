from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.fields import ArrayField

# Create your models here.

class User(AbstractUser):
    first_name = models.CharField('first name', max_length=150)
    last_name = models.CharField('last name', max_length=150)
    photo = models.ImageField('photo', upload_to='user_photos/' ,null=True, blank=True)
    phone = models.CharField('phone', max_length=100, null=True, blank=True)
    bio = models.TextField('bio', null=True, blank=True)
    ips = ArrayField(models.GenericIPAddressField(), null=True, blank=True)
    email = models.EmailField("email address", unique=True)\
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return self.username

class BlockIpAdress(models.Model):
    ip_address = models.GenericIPAddressField()

    def __str__(self):
        return self.ip_address