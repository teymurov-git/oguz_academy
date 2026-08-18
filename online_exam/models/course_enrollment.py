from django.db import models


class CourseEnrollment(models.Model):
    class PaymentType(models.TextChoices):
        MONTHLY = "monthly", "Aylıq"
        FULL = "full", "Tam"
        INSTALLMENT = "installment", "Taksit"

    student = models.ForeignKey(
        "online_exam.StudentCabinet", on_delete=models.CASCADE,
        related_name="course_enrollments", verbose_name="Şagird",
    )
    payment_type = models.CharField(
        max_length=20, choices=PaymentType.choices,
        default=PaymentType.MONTHLY, verbose_name="Ödəniş növü",
    )
    monthly_payment = models.DecimalField(
        max_digits=10, decimal_places=2, default=0,
        verbose_name="Aylıq ödəniş",
    )
    next_payment_date = models.DateField(
        null=True, blank=True, verbose_name="Növbəti ödəniş tarixi",
    )
    is_active = models.BooleanField(default=True, verbose_name="Aktivdir?")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Kurs qeydiyyatı"
        verbose_name_plural = "Kurs qeydiyyatları"

    def __str__(self):
        return f"{self.student} ({self.get_payment_type_display()})"


class CourseTeacherSchedule(models.Model):
    teacher = models.ForeignKey(
        "teachers.Teacher", on_delete=models.CASCADE,
        related_name="course_schedules", verbose_name="Müəllim",
    )
    days_times = models.JSONField(
        default=dict, blank=True,
        verbose_name="Günlər və saatlar",
        help_text='{"monday": "09:00-11:00", "wednesday": "09:00-11:00"}',
    )
    monthly_payment = models.DecimalField(
        max_digits=10, decimal_places=2, default=0,
        verbose_name="Aylıq ödəniş",
    )

    class Meta:
        verbose_name = "Kurs müəllim cədvəli"
        verbose_name_plural = "Kurs müəllim cədvəlləri"

    def __str__(self):
        return f"{self.teacher}"


class CoursePaymentRecord(models.Model):
    enrollment = models.ForeignKey(
        CourseEnrollment, on_delete=models.CASCADE,
        related_name="payment_records", verbose_name="Qeydiyyat",
    )
    amount = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="Məbləğ",
    )
    payment_date = models.DateField(verbose_name="Ödəniş tarixi")
    month_year = models.CharField(
        max_length=7, verbose_name="Ay/il",
        help_text="format: YYYY-MM",
    )
    notes = models.TextField(blank=True, default="", verbose_name="Qeydlər")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Kurs ödəniş qeydi"
        verbose_name_plural = "Kurs ödəniş qeydləri"

    def __str__(self):
        return f"{self.enrollment} — {self.month_year}: {self.amount}"
