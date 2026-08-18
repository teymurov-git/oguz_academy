import uuid
from django.db import models
from django.conf import settings


class Payment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Gözləyir'),
        ('paid', 'Ödənilib'),
        ('overdue', 'Gecikmiş'),
        ('cancelled', 'Ləğv olunub'),
        ('refunded', 'Geri qaytarılıb'),
    ]
    METHOD_CHOICES = [
        ('cash', 'Nağd'),
        ('card', 'Kart'),
        ('bank_transfer', 'Bank köçürməsi'),
        ('pos', 'POS'),
        ('other', 'Digər'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey('students.Student', on_delete=models.CASCADE, related_name='payments', verbose_name='Tələbə')
    groups = models.ManyToManyField('courses.Group', blank=True, related_name='payments', verbose_name='Qruplar')
    amount = models.DecimalField('Məbləğ', max_digits=10, decimal_places=2)
    paid_amount = models.DecimalField('Ödənilən məbləğ', max_digits=10, decimal_places=2, default=0)
    currency = models.CharField('Valyuta', max_length=3, default='AZN')
    payment_method = models.CharField('Ödəniş üsulu', max_length=20, choices=METHOD_CHOICES, default='cash')
    payment_date = models.DateField('Ödəniş tarixi', null=True, blank=True)
    due_date = models.DateField('Son tarix', null=True, blank=True)
    installment_number = models.IntegerField('Hissə nömrəsi', default=1)
    total_installments = models.IntegerField('Ümumi hissə', default=1)
    description = models.TextField('Təsvir', blank=True)
    receipt_number = models.CharField('Qəbiz nömrəsi', max_length=100, blank=True)
    status = models.CharField('Status', max_length=20, choices=STATUS_CHOICES, default='pending')
    collected_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='collected_payments', verbose_name='Toplayan')
    notes = models.TextField('Qeydlər', blank=True)
    is_active = models.BooleanField('Aktiv', default=True)
    created_at = models.DateTimeField('Yaradılma tarixi', auto_now_add=True)
    updated_at = models.DateTimeField('Yenilənmə tarixi', auto_now=True)

    class Meta:
        ordering = ('-created_at',)
        verbose_name = 'Ödəniş'
        verbose_name_plural = 'Ödənişlər'

    def __str__(self):
        return f"{self.student} - {self.amount} AZN"


class MonthlyPayment(models.Model):
    STATUS_CHOICES = [
        ('not_paid', 'Ödənməyib'),
        ('paid', 'Ödənilib'),
        ('overdue', 'Gecikib'),
    ]

    student = models.ForeignKey('students.Student', on_delete=models.CASCADE, related_name='monthly_payments', verbose_name='Tələbə')
    month = models.IntegerField('Ay')
    year = models.IntegerField('İl')
    status = models.CharField('Status', max_length=20, choices=STATUS_CHOICES, default='not_paid')
    amount = models.DecimalField('Məbləğ', max_digits=10, decimal_places=2)
    paid_at = models.DateTimeField('Ödənmə tarixi', null=True, blank=True)
    updated_at = models.DateTimeField('Yenilənmə tarixi', auto_now=True)

    class Meta:
        unique_together = ('student', 'month', 'year')
        ordering = ('year', 'month')
        verbose_name = 'Aylıq ödəniş'
        verbose_name_plural = 'Aylıq ödənişlər'

    def __str__(self):
        months_az = {1: 'Yan', 2: 'Fev', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'İyn', 7: 'İyl', 8: 'Avq', 9: 'Sen', 10: 'Okt', 11: 'Noy', 12: 'Dek'}
        return f"{self.student} - {months_az.get(self.month, '')} {self.year} - {self.get_status_display()}"


class PaymentPlan(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey('students.Student', on_delete=models.CASCADE, related_name='payment_plans', verbose_name='Tələbə')
    group = models.ForeignKey('courses.Group', on_delete=models.CASCADE, related_name='payment_plans', null=True, blank=True, verbose_name='Qrup')
    total_amount = models.DecimalField('Ümumi məbləğ', max_digits=10, decimal_places=2)
    total_installments = models.IntegerField('Ümumi hissə')
    installment_amount = models.DecimalField('Hissə məbləği', max_digits=10, decimal_places=2)
    start_date = models.DateField('Başlama tarixi')
    is_active = models.BooleanField('Aktiv', default=True)
    created_at = models.DateTimeField('Yaradılma tarixi', auto_now_add=True)

    class Meta:
        ordering = ('-created_at',)
        verbose_name = 'Ödəniş planı'
        verbose_name_plural = 'Ödəniş planları'

    def __str__(self):
        return f"{self.student} - {self.total_amount} AZN"
