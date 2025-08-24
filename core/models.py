from django.db import models

# Create your models here.

class AbstractModel(models.Model):

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class Contact(AbstractModel):
    first_name = models.CharField('firstname',max_length=100)
    last_name = models.CharField('lastname',max_length=100)
    email = models.EmailField('email',unique=False)
    phone = models.CharField('phone',max_length=15, blank=True, null=True)
    message = models.TextField('message',unique=False)

    def __str__(self):
        return self.first_name + ' ' + self.last_name
    
class Subscriber(AbstractModel):
    
    email = models.EmailField('email', max_length=200)

    def __str__(self):
        return self.email
        return self.email