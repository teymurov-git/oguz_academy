from django.db import models


class Payment(models.Model):
    METHOD_CHOICES = [
        ('cash', 'Nağd'),
        ('card', 'Kart'),
        ('transfer', 'Bank köçürməsi'),
        ('other', 'Digər'),
    ]

    student = models.ForeignKey('students.Student', on_delete=models.CASCADE, related_name='payments')
    group = models.ForeignKey('courses.Group', on_delete=models.SET_NULL, null=True, blank=True, related_name='payments')
    amount = models.DecimalField('amount', max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField('payment date', auto_now_add=True)
    payment_method = models.CharField('method', max_length=20, choices=METHOD_CHOICES, default='cash')
    note = models.TextField('note', blank=True)

    class Meta:
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'
        ordering = ('-payment_date',)

    def __str__(self):
        return f"{self.student} - {self.amount} AZN"
