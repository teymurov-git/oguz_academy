from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.fields import ArrayField

# Create your models here.

class User(AbstractUser):
    first_name = models.CharField('Ad', max_length=150)
    last_name = models.CharField('Soyad', max_length=150)
    photo = models.ImageField('Şəkil', upload_to='user_photos/', null=True, blank=True)
    phone = models.CharField('Telefon', max_length=100, null=True, blank=True)
    bio = models.TextField('Bioqrafiya', null=True, blank=True)
    ips = ArrayField(models.GenericIPAddressField(), null=True, blank=True, verbose_name='IP ünvanları')
    email = models.EmailField("Email ünvanı", unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return self.get_full_name() or self.username

    class Meta:
        verbose_name = 'İstifadəçi'
        verbose_name_plural = 'İstifadəçilər'


class BlockIpAdress(models.Model):
    ip_address = models.GenericIPAddressField('IP ünvanı')

    class Meta:
        verbose_name = 'Bloklanmış IP'
        verbose_name_plural = 'Bloklanmış IP-lər'

    def __str__(self):
        return self.ip_address