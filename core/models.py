from django.db import models

# Create your models here.

class AbstractModel(models.Model):

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class Contact(AbstractModel):
    first_name = models.CharField('first name', max_length=100)
    last_name = models.CharField('last name', max_length=100, blank=True, null=True)
    email = models.EmailField('email')
    phone = models.CharField('phone', max_length=100, blank=True, null=True)
    message = models.TextField('message')
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
class Subscriber(AbstractModel):
    
    email = models.EmailField('email', max_length=200)

    def __str__(self):
        return self.email