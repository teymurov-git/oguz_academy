import uuid
from django.db import models
from django.conf import settings
from django.utils.text import slugify


DEPARTMENT_CHOICES = [
    ('academic', 'Akademik'),
    ('finance', 'Maliyyə'),
    ('hr', 'HR'),
    ('marketing', 'Marketinq'),
    ('reception', 'Resepsiyon'),
    ('management', 'İdarəetmə'),
    ('other', 'Digər'),
]

SALARY_TYPE_CHOICES = [
    ('fixed', 'Sabit maaş'),
    ('per_student', 'Tələbə sayına görə'),
]


class Position(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField('Ad', max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    description = models.TextField('Təsvir', blank=True)
    is_active = models.BooleanField('Aktiv', default=True)
    created_at = models.DateTimeField('Yaradılma tarixi', auto_now_add=True)
    updated_at = models.DateTimeField('Yenilənmə tarixi', auto_now=True)

    class Meta:
        ordering = ('name',)
        verbose_name = 'Vəzifə'
        verbose_name_plural = 'Vəzifələr'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Employee(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='employee_profile', verbose_name='İstifadəçi')
    employee_id = models.PositiveIntegerField('İşçi ID', unique=True, null=True, blank=True, editable=False)
    department = models.CharField('Şöbə', max_length=100, choices=DEPARTMENT_CHOICES, default='other')
    position_fk = models.ForeignKey(Position, on_delete=models.SET_NULL, null=True, blank=True, related_name='employees', verbose_name='Vəzifə')
    phone = models.CharField('Telefon', max_length=50, blank=True)
    hire_date = models.DateField('İşə başlama tarixi', null=True, blank=True)
    salary_type = models.CharField('Maaş növü', max_length=20, choices=SALARY_TYPE_CHOICES, default='fixed')
    salary = models.DecimalField('Sabit maaş', max_digits=10, decimal_places=2, default=0)
    salary_per_student = models.DecimalField('Tələbə başına məbləğ', max_digits=10, decimal_places=2, null=True, blank=True)
    salary_percentage = models.DecimalField('Tələbə başına faiz', max_digits=5, decimal_places=2, null=True, blank=True)
    salary_currency = models.CharField('Valyuta', max_length=3, default='AZN')
    bank_account = models.CharField('Bank hesabı', max_length=50, blank=True)
    tax_number = models.CharField('VÖEN', max_length=50, blank=True)
    emergency_contact = models.JSONField('Təcili əlaqə', default=dict, blank=True)
    documents = models.JSONField('Sənədlər', default=list, blank=True)
    is_active = models.BooleanField('Aktiv', default=True)
    created_at = models.DateTimeField('Yaradılma tarixi', auto_now_add=True)
    updated_at = models.DateTimeField('Yenilənmə tarixi', auto_now=True)

    class Meta:
        ordering = ('-created_at',)
        verbose_name = 'İşçi'
        verbose_name_plural = 'İşçilər'

    def save(self, *args, **kwargs):
        if not self.employee_id:
            last = Employee.objects.order_by('employee_id').last()
            self.employee_id = (last.employee_id or 0) + 1 if last else 1001
        super().save(*args, **kwargs)

    def __str__(self):
        return self.user.get_full_name() or self.user.username
