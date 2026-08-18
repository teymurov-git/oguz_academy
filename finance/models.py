import uuid
from django.db import models
from django.conf import settings


class FinanceAccount(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField('Ad', max_length=200)
    account_type = models.CharField('Tip', max_length=50, choices=[
        ('cash', 'Nağd'),
        ('bank', 'Bank'),
        ('pos', 'POS terminal'),
        ('online', 'Online'),
    ])
    currency = models.CharField('Valyuta', max_length=3, default='AZN')
    balance = models.DecimalField('Balans', max_digits=15, decimal_places=2, default=0)
    is_active = models.BooleanField('Aktiv', default=True)
    created_at = models.DateTimeField('Yaradılma tarixi', auto_now_add=True)

    class Meta:
        ordering = ('name',)
        verbose_name = 'Maliyyə hesabı'
        verbose_name_plural = 'Maliyyə hesabları'

    def __str__(self):
        return f"{self.name} ({self.balance} AZN)"


class ExpenseCategory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField('Ad', max_length=200)
    description = models.TextField('Təsvir', blank=True)
    is_active = models.BooleanField('Aktiv', default=True)

    class Meta:
        ordering = ('name',)
        verbose_name = 'Xərc kateqoriyası'
        verbose_name_plural = 'Xərc kateqoriyaları'

    def __str__(self):
        return self.name


class Expense(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    category = models.ForeignKey(ExpenseCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='expenses', verbose_name='Kateqoriya')
    amount = models.DecimalField('Məbləğ', max_digits=10, decimal_places=2)
    currency = models.CharField('Valyuta', max_length=3, default='AZN')
    description = models.TextField('Təsvir')
    expense_date = models.DateField('Xərc tarixi')
    payment_method = models.CharField('Ödəniş üsulu', max_length=20, choices=[
        ('cash', 'Nağd'),
        ('card', 'Kart'),
        ('bank_transfer', 'Bank köçürməsi'),
    ], default='cash')
    receipt = models.ImageField('Qəbiz', upload_to='expenses/', null=True, blank=True)
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_expenses', verbose_name='Təsdiq edən')
    notes = models.TextField('Qeydlər', blank=True)
    is_active = models.BooleanField('Aktiv', default=True)
    created_at = models.DateTimeField('Yaradılma tarixi', auto_now_add=True)
    updated_at = models.DateTimeField('Yenilənmə tarixi', auto_now=True)

    class Meta:
        ordering = ('-expense_date',)
        verbose_name = 'Xərc'
        verbose_name_plural = 'Xərclər'

    def __str__(self):
        return f"{self.category} - {self.amount} AZN"


class Salary(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Gözləyir'),
        ('paid', 'Ödənilib'),
        ('cancelled', 'Ləğv olunub'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee = models.ForeignKey('employees.Employee', on_delete=models.CASCADE, related_name='salaries', verbose_name='İşçi')
    amount = models.DecimalField('Məbləğ', max_digits=10, decimal_places=2)
    bonus = models.DecimalField('Bonus', max_digits=10, decimal_places=2, default=0)
    deduction = models.DecimalField('Tutulma', max_digits=10, decimal_places=2, default=0)
    net_amount = models.DecimalField('Net məbləğ', max_digits=10, decimal_places=2)
    month = models.IntegerField('Ay')
    year = models.IntegerField('İl')
    payment_date = models.DateField('Ödəniş tarixi', null=True, blank=True)
    payment_method = models.CharField('Ödəniş üsulu', max_length=20, blank=True)
    status = models.CharField('Status', max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField('Qeydlər', blank=True)
    created_at = models.DateTimeField('Yaradılma tarixi', auto_now_add=True)
    updated_at = models.DateTimeField('Yenilənmə tarixi', auto_now=True)

    class Meta:
        ordering = ('-year', '-month')
        unique_together = ('employee', 'month', 'year')
        verbose_name = 'Maaş'
        verbose_name_plural = 'Maaşlar'

    def __str__(self):
        return f"{self.employee} - {self.month}/{self.year}"
