import secrets
from django.db import models
from django.conf import settings


class NotificationTemplate(models.Model):
    class NotificationType(models.TextChoices):
        EXAM = "exam", "İmtahan"
        RESULT = "result", "Nəticə"
        ANNOUNCEMENT = "announcement", "Elan"
        SYSTEM = "system", "Sistem"
        MESSAGE = "message", "Mesaj"
        PAYMENT = "payment", "Ödəniş"
        STATUS = "status", "Status"

    name = models.CharField(max_length=255, verbose_name="Şablon adı")
    title = models.CharField(max_length=255, verbose_name="Başlıq")
    message = models.TextField(verbose_name="Mesaj")
    notification_type = models.CharField(
        max_length=20, choices=NotificationType.choices,
        default=NotificationType.SYSTEM, verbose_name="Bildiriş tipi",
    )

    class Meta:
        verbose_name = "Bildiriş şablonu"
        verbose_name_plural = "Bildiriş şablonları"

    def __str__(self):
        return self.name


class CabinetNotification(models.Model):
    title = models.CharField(max_length=255, verbose_name="Başlıq")
    message = models.TextField(verbose_name="Mesaj")
    is_read = models.BooleanField(default=False, verbose_name="Oxunub?")
    link = models.CharField(max_length=500, blank=True, default="", verbose_name="Keçid")
    template = models.ForeignKey(
        NotificationTemplate, on_delete=models.SET_NULL,
        null=True, blank=True, verbose_name="Şablon",
    )
    student = models.ForeignKey(
        "online_exam.StudentCabinet", on_delete=models.CASCADE,
        related_name="notifications", verbose_name="Şagird",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Kabinet bildirişi"
        verbose_name_plural = "Kabinet bildirişləri"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} → {self.student}"


class CabinetActivity(models.Model):
    class ActivityType(models.TextChoices):
        EXAM_START = "exam_start", "İmtahan başladı"
        SUBMIT = "submit", "Təqdim edildi"
        ASSIGNED = "assigned", "Təyin edildi"

    student = models.ForeignKey(
        "online_exam.StudentCabinet", on_delete=models.CASCADE,
        related_name="activities", verbose_name="Şagird",
    )
    activity_type = models.CharField(
        max_length=20, choices=ActivityType.choices, verbose_name="Fəaliyyət növü",
    )
    exam_name = models.CharField(max_length=255, blank=True, default="", verbose_name="İmtahan adı")
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name="IP ünvanı")
    user_agent = models.TextField(blank=True, default="", verbose_name="User Agent")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Kabinet fəaliyyəti"
        verbose_name_plural = "Kabinet fəaliyyətləri"
        ordering = ["-created_at"]


class LoginAttempt(models.Model):
    identifier = models.CharField(max_length=255, verbose_name="Identifikator")
    identifier_type = models.CharField(
        max_length=20, verbose_name="Identifikator tipi",
        help_text="work_number / email / username",
    )
    ip_address = models.GenericIPAddressField(verbose_name="IP ünvanı")
    is_successful = models.BooleanField(default=False, verbose_name="Uğurludur?")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Login cəhdi"
        verbose_name_plural = "Login cəhdləri"
        ordering = ["-created_at"]


class LoginBlock(models.Model):
    identifier = models.CharField(max_length=255, unique=True, verbose_name="Identifikator")
    blocked_until = models.DateTimeField(verbose_name="Bloklanma müddəti")
    attempt_count = models.PositiveIntegerField(default=0, verbose_name="Cəhd sayı")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Login bloku"
        verbose_name_plural = "Login blokları"

    def __str__(self):
        return f"{self.identifier} — blok {self.blocked_until}-a qədər"


class PasswordResetOTP(models.Model):
    email = models.EmailField(verbose_name="Email")
    otp_code = models.CharField(max_length=6, verbose_name="OTP kodu")
    purpose = models.CharField(
        max_length=50, verbose_name="Məqsəd",
        help_text="password_reset / work_number_recovery",
    )
    is_used = models.BooleanField(default=False, verbose_name="İstifadə olunub?")
    expires_at = models.DateTimeField(verbose_name="Bitmə vaxtı")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Şifrə sıfırlama OTP"
        verbose_name_plural = "Şifrə sıfırlama OTP-ləri"

    def save(self, *args, **kwargs):
        if not self.otp_code:
            self.otp_code = f"{secrets.randbelow(1000000):06d}"
        super().save(*args, **kwargs)


class WhatsAppTemplate(models.Model):
    class TemplateType(models.TextChoices):
        INFO = "info", "Məlumat"
        PAYMENT = "payment", "Ödəniş"
        ONLINE = "online", "Online imtahan"

    exam = models.ForeignKey(
        "online_exam.Exam", on_delete=models.CASCADE,
        related_name="whatsapp_templates", verbose_name="İmtahan",
    )
    name = models.CharField(max_length=255, verbose_name="Şablon adı")
    message_template = models.TextField(verbose_name="Mesaj şablonu")
    template_type = models.CharField(
        max_length=20, choices=TemplateType.choices,
        default=TemplateType.INFO, verbose_name="Şablon tipi",
    )

    class Meta:
        verbose_name = "WhatsApp şablonu"
        verbose_name_plural = "WhatsApp şablonları"

    def __str__(self):
        return f"{self.name} ({self.get_template_type_display()})"


class ExamRecording(models.Model):
    class RecordingType(models.TextChoices):
        COMBINED = "combined", "Ekran+kamera"
        SCREEN = "screen", "Ekran"
        CAMERA = "camera", "Kamera"

    assignment = models.ForeignKey(
        "online_exam.OnlineExamAssignment", on_delete=models.CASCADE,
        related_name="recordings", verbose_name="Təyinat",
    )
    session = models.ForeignKey(
        "online_exam.StudentExamSession", on_delete=models.CASCADE,
        null=True, blank=True, verbose_name="Seans",
    )
    student = models.ForeignKey(
        "online_exam.StudentCabinet", on_delete=models.CASCADE,
        verbose_name="Şagird",
    )
    recording_type = models.CharField(
        max_length=20, choices=RecordingType.choices,
        default=RecordingType.COMBINED, verbose_name="Yazısı növü",
    )
    video_file = models.FileField(
        upload_to="exam_recordings/", verbose_name="Video faylı",
    )
    file_size = models.PositiveBigIntegerField(default=0, verbose_name="Fayl ölçüsü (bayt)")
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name="Yüklənmə tarixi")

    class Meta:
        verbose_name = "İmtahan yazısı"
        verbose_name_plural = "İmtahan yazıları"

    def __str__(self):
        return f"{self.student} — {self.get_recording_type_display()}"
