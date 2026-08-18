from django.db import models
from django.conf import settings


class Exam(models.Model):
    class PaymentType(models.TextChoices):
        CASH = "cash", "Yalnız Nağd"
        CARD = "card", "Yalnız Kart"
        CARD_AND_CASH = "card_and_cash", "Həm Kart, Həm Nağd"

    exam_id = models.BigAutoField(primary_key=True, verbose_name="İmtahan ID")
    exam_name = models.CharField(max_length=255, verbose_name="İmtahan adı")
    exam_date = models.DateField(verbose_name="İmtahan tarixi")
    exam_image = models.ImageField(
        upload_to="exam_images/", null=True, blank=True, verbose_name="Şəkil",
    )

    exam_type = models.ForeignKey(
        "ExamType", on_delete=models.SET_NULL, null=True, blank=True,
        verbose_name="İmtahan tipi",
    )
    exam_subject = models.JSONField(
        default=list, blank=True,
        verbose_name="Fənlər (snapshot)",
        help_text='[{"subject": "Riyaziyyat", "count": 30}, ...]',
    )
    exam_pricing = models.JSONField(
        default=list, blank=True,
        verbose_name="Qiymət cədvəli",
        help_text='[{"branch_id": 1, "price_course": 15, "price_other": 20}, ...]',
    )
    exam_variants = models.JSONField(
        default=list, blank=True,
        verbose_name="Variantlar",
    )

    exam_classes = models.ManyToManyField(
        "online_exam.Sinif", blank=True, verbose_name="Siniflər",
    )
    exam_sections = models.ManyToManyField(
        "online_exam.Bolme", blank=True, verbose_name="Bölmələr",
    )
    exam_groups = models.ManyToManyField(
        "online_exam.Qrup", blank=True, verbose_name="Qruplar",
    )

    available_previous_exams = models.ManyToManyField(
        "PreviousExam", blank=True, verbose_name="Seçilə bilən əvvəlki imtahanlar",
    )

    exam_register = models.BooleanField(default=False, verbose_name="Qeydiyyat açıqdır?")
    exam_result = models.BooleanField(default=False, verbose_name="Nəticələr görünürmü?")
    does_answers_added = models.BooleanField(default=False, verbose_name="Cavab açarı əlavə olunub?")
    exam_register_count = models.PositiveIntegerField(default=0, verbose_name="Qeydiyyat sayı")

    payment_type = models.CharField(
        max_length=20, choices=PaymentType.choices,
        default=PaymentType.CASH, verbose_name="Ödəniş növü",
    )

    proctor_screen_recording = models.BooleanField(default=False, verbose_name="Ekran yazısı")
    proctor_camera_recording = models.BooleanField(default=False, verbose_name="Kamera yazısı")
    proctor_copy_paste_block = models.BooleanField(default=False, verbose_name="Copy/paste blok")

    exam_guide = models.TextField(blank=True, default="", verbose_name="İmtahan təlimatı")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "İmtahan"
        verbose_name_plural = "İmtahanlar"
        ordering = ["-exam_date"]

    def __str__(self):
        return f"{self.exam_name} ({self.exam_date})"


class CorrectAnswerKey(models.Model):
    key_id = models.BigAutoField(primary_key=True, verbose_name="Açar ID")

    exam = models.ForeignKey(
        Exam, on_delete=models.CASCADE, related_name="answer_keys",
        verbose_name="İmtahan",
    )
    subject = models.ForeignKey(
        "Subject", on_delete=models.CASCADE, verbose_name="Fənn",
    )
    variant_name = models.CharField(max_length=100, verbose_name="Variant adı")
    subject_order = models.PositiveIntegerField(default=0, verbose_name="Fənn sırası")

    sinif = models.ForeignKey(
        "Sinif", on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Sinif",
    )
    bolme = models.ForeignKey(
        "Bolme", on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Bölmə",
    )
    qrup = models.ForeignKey(
        "Qrup", on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Qrup",
    )

    answers_data = models.JSONField(
        default=list, verbose_name="Sual siyahısı",
        help_text="""
        [
            {
                "question_number": 1,
                "correct_answer": "A",
                "question_type": "Qapalı",
                "question_text": "...",
                "question_image": "",
                "audio_url": "",
                "points": 5.0,
                "penalty_points": 0.0,
                "is_choice": false,
                "is_starred": false,
                "marker_check": false
            }
        ]
        """,
    )

    is_online = models.BooleanField(default=False, verbose_name="Online imtahandır?")
    online_start_date = models.DateField(null=True, blank=True, verbose_name="Online başlama tarixi")
    online_start_time = models.TimeField(null=True, blank=True, verbose_name="Online başlama saatı")
    online_end_date = models.DateField(null=True, blank=True, verbose_name="Online bitmə tarixi")
    online_end_time = models.TimeField(null=True, blank=True, verbose_name="Online bitmə saatı")
    online_duration_hours = models.FloatField(
        default=3, verbose_name="Online müddət (saat)",
    )
    online_cover_image = models.ImageField(
        upload_to="exam_covers/", null=True, blank=True, verbose_name="Online örtük şəkli",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Cavab açarı"
        verbose_name_plural = "Cavab açarları"
        unique_together = ["exam", "variant_name", "subject", "sinif", "bolme", "qrup"]
        ordering = ["exam", "variant_name", "subject_order"]

    def __str__(self):
        return f"{self.exam} | {self.variant_name} | {self.subject} | order={self.subject_order}"


class ExamSessions(models.Model):
    exam = models.ForeignKey(
        Exam, on_delete=models.CASCADE, related_name="sessions",
        verbose_name="İmtahan",
    )
    time = models.TimeField(verbose_name="Seans saatı")
    session_yer_count = models.PositiveIntegerField(
        default=30, verbose_name="Yer sayı",
    )

    class Meta:
        verbose_name = "İmtahan seansı"
        verbose_name_plural = "İmtahan seansları"
        unique_together = ["exam", "time"]

    def __str__(self):
        return f"{self.exam} | {self.time}"
