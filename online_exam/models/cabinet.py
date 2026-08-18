import secrets
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator


class StudentCabinet(models.Model):
    class Gender(models.TextChoices):
        MALE = "male", "Kişi"
        FEMALE = "female", "Qadın"

    class VerificationStatus(models.TextChoices):
        NONE = "none", "Heç biri"
        PENDING = "pending", "Gözləmədə"
        APPROVED = "approved", "Təsdiqləndi"
        REJECTED = "rejected", "Rədd edildi"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name="student_cabinet", verbose_name="İstifadəçi",
    )
    work_number = models.PositiveIntegerField(
        unique=True,
        validators=[MinValueValidator(100000), MaxValueValidator(999999)],
        verbose_name="İş nömrəsi",
        help_text="6 rəqəmli unikal identifikator",
    )

    phone = models.CharField(max_length=20, blank=True, default="", verbose_name="Telefon")
    birth_date = models.DateField(null=True, blank=True, verbose_name="Doğum tarixi")
    parent_phone = models.CharField(max_length=20, blank=True, default="", verbose_name="Valideyn telefonu")
    father_name = models.CharField(max_length=100, blank=True, default="", verbose_name="Ata adı")
    gender = models.CharField(
        max_length=10, choices=Gender.choices,
        default=Gender.MALE, verbose_name="Cins",
    )
    profile_image = models.ImageField(
        upload_to="student_profiles/", null=True, blank=True, verbose_name="Profil şəkli",
    )
    selected_avatar = models.CharField(
        max_length=10, default="neutral",
        verbose_name="Seçilmiş avatar",
    )

    school_new = models.ForeignKey(
        "online_exam.School", on_delete=models.SET_NULL,
        null=True, blank=True, verbose_name="Məktəb",
    )
    district = models.ForeignKey(
        "online_exam.District", on_delete=models.SET_NULL,
        null=True, blank=True, verbose_name="Rayon",
    )
    sinif = models.CharField(max_length=100, blank=True, default="", verbose_name="Sinif")
    qrup = models.CharField(max_length=100, blank=True, default="", verbose_name="Qrup")
    bolme = models.CharField(max_length=100, blank=True, default="", verbose_name="Bölmə")
    region = models.CharField(max_length=100, blank=True, default="", verbose_name="Region (legacy)")

    is_course_student = models.BooleanField(default=False, verbose_name="Kurs şagirdidir?")
    course_teachers = models.ManyToManyField(
        "teachers.Teacher", blank=True, verbose_name="Kurs müəllimləri",
    )

    student_verification_status = models.CharField(
        max_length=20, choices=VerificationStatus.choices,
        default=VerificationStatus.NONE, verbose_name="Təsdiq statusu",
    )
    pending_verification_teacher_ids = models.JSONField(
        default=list, blank=True, verbose_name="Gözləyən müəllim ID-ləri",
    )
    student_id_number = models.CharField(
        max_length=20, blank=True, default="", verbose_name="Şəxsiyyət nömrəsi",
    )

    is_active = models.BooleanField(default=True, verbose_name="Aktivdir?")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Şagird kabineti"
        verbose_name_plural = "Şagird kabinetləri"

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.work_number})"

    def save(self, *args, **kwargs):
        if not self.work_number:
            while True:
                num = secrets.randbelow(900000) + 100000
                if not StudentCabinet.objects.filter(work_number=num).exists():
                    self.work_number = num
                    break
        super().save(*args, **kwargs)


class ExamParticipation(models.Model):
    class Status(models.TextChoices):
        REGISTERED = "registered", "Qeydiyyatda"
        ACTIVE = "active", "Aktiv"
        COMPLETED = "completed", "Tamamlandı"
        CANCELLED = "cancelled", "Ləğv edildi"

    student = models.ForeignKey(
        StudentCabinet, on_delete=models.CASCADE,
        related_name="participations", verbose_name="Şagird",
    )
    exam = models.ForeignKey(
        "online_exam.Exam", on_delete=models.CASCADE,
        related_name="participations", verbose_name="İmtahan",
    )
    register = models.ForeignKey(
        "online_exam.Register", on_delete=models.SET_NULL,
        null=True, blank=True, verbose_name="Qeydiyyat",
    )
    is_quiz = models.BooleanField(default=False, verbose_name="Quizdir?")

    status = models.CharField(
        max_length=20, choices=Status.choices,
        default=Status.REGISTERED, verbose_name="Status",
    )
    attempt_count = models.PositiveIntegerField(default=0, verbose_name="Cəhd sayı")
    last_attempt_number = models.PositiveIntegerField(default=0, verbose_name="Son cəhd nömrəsi")
    last_attempt_type = models.CharField(max_length=20, blank=True, default="", verbose_name="Son cəhd növü")
    last_attempt_at = models.DateTimeField(null=True, blank=True, verbose_name="Son cəhd tarixi")

    score = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, verbose_name="Bal",
    )
    max_score = models.DecimalField(
        max_digits=10, decimal_places=2, default=100, verbose_name="Maksimum bal",
    )
    exam_name = models.CharField(max_length=255, blank=True, default="", verbose_name="İmtahan adı")
    exam_date = models.DateField(null=True, blank=True, verbose_name="İmtahan tarixi")
    is_online = models.BooleanField(default=False, verbose_name="Online imtahandır?")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "İmtahan iştirakı"
        verbose_name_plural = "İmtahan iştirakları"
        unique_together = [["student", "exam", "is_quiz"]]

    def __str__(self):
        return f"{self.student} → {self.exam_name or self.exam} (quiz={self.is_quiz})"


class ExamAttempt(models.Model):
    class AttemptType(models.TextChoices):
        OFFLINE = "offline", "Əyani import"
        ONLINE = "online", "Online kabinet"
        MANUAL = "manual", "Manual"

    participation = models.ForeignKey(
        ExamParticipation, on_delete=models.CASCADE,
        related_name="attempts", verbose_name="İştirak",
    )
    attempt_number = models.PositiveIntegerField(default=1, verbose_name="Cəhd nömrəsi")
    attempt_type = models.CharField(
        max_length=20, choices=AttemptType.choices,
        default=AttemptType.ONLINE, verbose_name="Cəhd növü",
    )

    assignment = models.OneToOneField(
        "OnlineExamAssignment", on_delete=models.SET_NULL,
        null=True, blank=True, verbose_name="Təyinat",
    )
    sagird_result = models.OneToOneField(
        "online_exam.SagirdResult", on_delete=models.SET_NULL,
        null=True, blank=True, verbose_name="Nəticə",
    )
    register = models.ForeignKey(
        "online_exam.Register", on_delete=models.SET_NULL,
        null=True, blank=True, verbose_name="Qeydiyyat",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "İmtahan cəhdi"
        verbose_name_plural = "İmtahan cəhdləri"
        ordering = ["attempt_number"]

    def __str__(self):
        return f"{self.participation} — cəhd {self.attempt_number}"


class OnlineExamAssignment(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "active", "Aktiv"
        INACTIVE = "inactive", "Deaktiv"
        SUBMITTED = "submitted", "Təqdim edildi"
        COMPLETED = "completed", "Tamamlandı (arxiv)"

    class ExamTypeChoice(models.TextChoices):
        EXAM = "exam", "İmtahan"
        QUIZ = "quiz", "Quiz"

    student = models.ForeignKey(
        StudentCabinet, on_delete=models.CASCADE,
        related_name="exam_assignments", verbose_name="Şagird",
    )
    exam_name = models.CharField(max_length=255, verbose_name="İmtahan adı")
    exam_description = models.TextField(blank=True, default="", verbose_name="Təsvir")
    exam_date = models.DateField(verbose_name="İmtahan tarixi")
    duration_minutes = models.PositiveIntegerField(default=180, verbose_name="Müddət (dəqiqə)")
    max_score = models.DecimalField(
        max_digits=10, decimal_places=2, default=100, verbose_name="Maksimum bal",
    )

    status = models.CharField(
        max_length=20, choices=Status.choices,
        default=Status.ACTIVE, verbose_name="Status",
    )
    exam_type = models.CharField(
        max_length=10, choices=ExamTypeChoice.choices,
        default=ExamTypeChoice.EXAM, verbose_name="İmtahan növü",
    )
    is_quiz = models.BooleanField(default=False, verbose_name="Quizdir?")

    exam_id = models.IntegerField(verbose_name="İmtahan ID")
    variant_name = models.CharField(max_length=100, blank=True, default="", verbose_name="Variant")

    sinif = models.ForeignKey(
        "online_exam.Sinif", on_delete=models.SET_NULL,
        null=True, blank=True, verbose_name="Sinif",
    )
    bolme = models.ForeignKey(
        "online_exam.Bolme", on_delete=models.SET_NULL,
        null=True, blank=True, verbose_name="Bölmə",
    )
    qrup = models.ForeignKey(
        "online_exam.Qrup", on_delete=models.SET_NULL,
        null=True, blank=True, verbose_name="Qrup",
    )

    register = models.ForeignKey(
        "online_exam.Register", on_delete=models.SET_NULL,
        null=True, blank=True, verbose_name="Qeydiyyat",
    )
    participation = models.ForeignKey(
        ExamParticipation, on_delete=models.SET_NULL,
        null=True, blank=True, verbose_name="İştirak",
    )
    sagird_result = models.ForeignKey(
        "online_exam.SagirdResult", on_delete=models.SET_NULL,
        null=True, blank=True, verbose_name="Nəticə",
    )
    result_generated_at = models.DateTimeField(null=True, blank=True, verbose_name="Nəticə yaradılma tarixi")

    prep_timer_started_at = models.DateTimeField(null=True, blank=True, verbose_name="Hazırlıq taymeri başlama")
    prep_timer_completed = models.BooleanField(default=False, verbose_name="Hazırlıq taymeri bitib")

    attempt_number = models.PositiveIntegerField(default=1, verbose_name="Cəhd nömrəsi")
    parent_assignment = models.ForeignKey(
        "self", on_delete=models.SET_NULL,
        null=True, blank=True, verbose_name="Əsas təyinat",
    )

    proctor_screen_recording = models.BooleanField(default=False, verbose_name="Ekran yazısı")
    proctor_camera_recording = models.BooleanField(default=False, verbose_name="Kamera yazısı")
    proctor_copy_paste_block = models.BooleanField(default=False, verbose_name="Copy/paste blok")

    can_view_result = models.BooleanField(default=True, verbose_name="Nəticəni görmək olar?")
    result_hidden_at = models.DateTimeField(null=True, blank=True, verbose_name="Nəticə gizləndi tarixi")
    result_hidden_by = models.CharField(
        max_length=255, blank=True, default="", verbose_name="Nəticəni kim gizlətdi",
    )

    is_visible = models.BooleanField(default=True, verbose_name="Görünür?")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Online imtahan təyinatı"
        verbose_name_plural = "Online imtahan təyinatları"
        unique_together = [["student", "exam_id", "variant_name", "attempt_number"]]

    def __str__(self):
        return f"{self.student} → {self.exam_name} (cəhd {self.attempt_number})"


class StudentExamSession(models.Model):
    assignment = models.OneToOneField(
        OnlineExamAssignment, on_delete=models.CASCADE,
        related_name="session", verbose_name="Təyinat",
    )
    started_at = models.DateTimeField(auto_now_add=True, verbose_name="Başlama vaxtı")
    submitted_at = models.DateTimeField(null=True, blank=True, verbose_name="Təqdim tarixi")
    is_submitted = models.BooleanField(default=False, verbose_name="Təqdim edilib?")

    result = models.OneToOneField(
        "online_exam.SagirdResult", on_delete=models.SET_NULL,
        null=True, blank=True, verbose_name="Nəticə",
    )

    class Meta:
        verbose_name = "İmtahan seansı"
        verbose_name_plural = "İmtahan seansları"

    def __str__(self):
        return f"Seans: {self.assignment}"


class StudentAnswer(models.Model):
    session = models.ForeignKey(
        StudentExamSession, on_delete=models.CASCADE,
        related_name="answers", verbose_name="Seans",
    )
    question_number = models.PositiveIntegerField(verbose_name="Sual nömrəsi")
    subject = models.CharField(max_length=255, verbose_name="Fənn")
    question_type = models.CharField(max_length=100, verbose_name="Sual tipi")
    answer = models.TextField(blank=True, default="", verbose_name="Cavab")
    answered_at = models.DateTimeField(auto_now_add=True, verbose_name="Cavab tarixi")

    class Meta:
        verbose_name = "Şagird cavabı"
        verbose_name_plural = "Şagird cavabları"
        unique_together = [["session", "question_number", "subject"]]

    def __str__(self):
        return f"Q{self.question_number} ({self.subject}): {self.answer}"
