from django.db import models


class Register(models.Model):
    class PaymentStatus(models.TextChoices):
        PENDING_CARD = "pending_card", "Kart gözləyir"
        PENDING_CASH = "pending_cash", "Nağd gözləyir"
        SUCCESS = "success", "Uğurlu"
        FAILED = "failed", "Uğursuz"
        REFUNDED = "refunded", "Geri qaytarıldı"

    class PaymentMethod(models.TextChoices):
        CARD = "card", "Kart"
        CASH = "cash", "Nağd"

    id = models.BigAutoField(primary_key=True)

    first_name = models.CharField(max_length=100, verbose_name="Ad")
    last_name = models.CharField(max_length=100, verbose_name="Soyad")
    father_name = models.CharField(max_length=100, blank=True, default="", verbose_name="Ata adı")
    phone = models.CharField(max_length=20, verbose_name="Telefon")
    gender = models.CharField(max_length=10, blank=True, default="", verbose_name="Cins")

    student_reg_number = models.CharField(
        max_length=10, blank=True, default="",
        verbose_name="İş nömrəsi",
    )

    student_class = models.CharField(max_length=255, blank=True, default="", verbose_name="Sinif")
    student_section = models.CharField(max_length=255, blank=True, default="", verbose_name="Bölmə")
    student_group = models.CharField(max_length=255, blank=True, default="", verbose_name="Qrup")

    exam_id = models.IntegerField(verbose_name="İmtahan ID")

    selected_previous_exams = models.ManyToManyField(
        "PreviousExam", blank=True, verbose_name="Seçilmiş əvvəlki imtahanlar",
    )

    student_total_price = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, verbose_name="Ümumi qiymət",
    )
    student_payment = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, verbose_name="Ödənilən məbləğ",
    )
    is_paid = models.BooleanField(default=False, verbose_name="Ödənilib?")
    payment_status = models.CharField(
        max_length=20, choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING_CASH, verbose_name="Ödəniş statusu",
    )
    payment_method = models.CharField(
        max_length=10, choices=PaymentMethod.choices,
        blank=True, default="", verbose_name="Ödəniş üsulu",
    )
    transaction_id = models.CharField(
        max_length=255, blank=True, default="", verbose_name="Tranzaksiya ID",
    )
    payment_date = models.DateTimeField(null=True, blank=True, verbose_name="Ödəniş tarixi")

    has_incomplete_data = models.BooleanField(default=False, verbose_name="Natamam məlumat")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Qeydiyyat"
        verbose_name_plural = "Qeydiyyatlar"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.last_name} {self.first_name} | exam={self.exam_id}"
