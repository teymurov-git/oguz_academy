from django.db import models
from django.contrib.auth.hashers import make_password, check_password


class Marker(models.Model):
    class Role(models.TextChoices):
        MARKER = "marker", "Marker"
        HEAD_MARKER = "head_marker", "Baş Marker"

    name = models.CharField(max_length=255, verbose_name="Ad")
    email = models.EmailField(unique=True, verbose_name="Email")
    password = models.CharField(max_length=255, verbose_name="Şifrə (hash)")
    is_active = models.BooleanField(default=True, verbose_name="Aktivdir?")

    role = models.CharField(
        max_length=20, choices=Role.choices,
        default=Role.MARKER, verbose_name="Rol",
    )
    allowed_subjects = models.ManyToManyField(
        "online_exam.Subject", blank=True, verbose_name="İzin verilən fənlər",
    )

    last_login_at = models.DateTimeField(null=True, blank=True, verbose_name="Son giriş")

    class Meta:
        verbose_name = "Marker (Yoxlayıcı)"
        verbose_name_plural = "Markerlər"

    def __str__(self):
        return f"{self.name} ({self.get_role_display()})"

    @property
    def is_head_marker(self):
        return self.role == self.Role.HEAD_MARKER

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)


class QuestionAssignment(models.Model):
    exam = models.ForeignKey(
        "online_exam.Exam", on_delete=models.CASCADE,
        related_name="question_assignments", verbose_name="İmtahan",
    )
    subject = models.ForeignKey(
        "online_exam.Subject", on_delete=models.CASCADE,
        verbose_name="Fənn",
    )
    question_number = models.PositiveIntegerField(verbose_name="Sual nömrəsi")

    required_marker_count = models.PositiveIntegerField(
        default=1, verbose_name="Tələb olunan marker sayı",
    )
    assigned_markers = models.ManyToManyField(
        Marker, blank=True, related_name="assignments", verbose_name="Təyin olunmuş markerlər",
    )
    head_marker = models.ForeignKey(
        Marker, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="head_assignments",
        verbose_name="Baş marker",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Sual təyinatı"
        verbose_name_plural = "Sual təyinatları"
        unique_together = ["exam", "subject", "question_number"]

    def __str__(self):
        return f"{self.exam} | {self.subject} | Q{self.question_number}"


class StudentAnswerGrading(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Gözləyir"
        IN_PROGRESS = "in_progress", "Davam edir"
        HEAD_MARKER = "head_marker", "Baş Markerə"
        FINALIZED = "finalized", "Tamamlandı"

    result = models.ForeignKey(
        "online_exam.SagirdResult", on_delete=models.CASCADE,
        related_name="answer_gradings", verbose_name="Nəticə",
    )
    assignment = models.ForeignKey(
        QuestionAssignment, on_delete=models.CASCADE,
        related_name="gradings", verbose_name="Sual təyinatı",
    )
    subject_name = models.CharField(max_length=255, verbose_name="Fənn adı")
    question_number = models.PositiveIntegerField(verbose_name="Sual nömrəsi")

    status = models.CharField(
        max_length=20, choices=Status.choices,
        default=Status.PENDING, verbose_name="Status",
    )
    final_score = models.DecimalField(
        max_digits=10, decimal_places=3, default=0,
        verbose_name="Son ball",
    )
    final_fraction = models.CharField(
        max_length=10, blank=True, default="",
        verbose_name="Son fraksiya",
    )
    is_suspicious = models.BooleanField(default=False, verbose_name="Şübhəlidir?")
    current_marker_index = models.PositiveIntegerField(default=0, verbose_name="Cari marker indeksi")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Cavab qiymətləndirməsi"
        verbose_name_plural = "Cavab qiymətləndirmələri"
        unique_together = ["result", "subject_name", "question_number"]

    def __str__(self):
        return f"Q{self.question_number} ({self.subject_name}) — {self.get_status_display()}"


class IndividualGrade(models.Model):
    answer_grading = models.ForeignKey(
        StudentAnswerGrading, on_delete=models.CASCADE,
        related_name="individual_grades", verbose_name="Qiymətləndirmə",
    )
    marker = models.ForeignKey(
        Marker, on_delete=models.CASCADE,
        related_name="grades", verbose_name="Marker",
    )

    fraction = models.CharField(
        max_length=10, verbose_name="Fraksiya",
        help_text="0, 1/3, 1/2, 2/3, 1",
    )
    numeric_score = models.DecimalField(
        max_digits=10, decimal_places=3, default=0,
        verbose_name="Rəqəmsal ball",
    )
    max_points = models.DecimalField(
        max_digits=10, decimal_places=2, default=0,
        verbose_name="Maksimum ball",
    )

    is_suspicious = models.BooleanField(default=False, verbose_name="Şübhəlidir?")
    is_head_marker_override = models.BooleanField(default=False, verbose_name="Baş marker override")
    notes = models.TextField(blank=True, default="", verbose_name="Qeydlər")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Fərdi qiymət"
        verbose_name_plural = "Fərdi qiymətlər"
        unique_together = ["answer_grading", "marker"]

    def __str__(self):
        return f"{self.marker.name}: {self.fraction} ({self.answer_grading})"


class MarkerAnswerGrade(models.Model):
    """Köhnə tək-marker modeli — geriyə uyğunluq üçün saxlanılır."""
    result = models.ForeignKey(
        "online_exam.SagirdResult", on_delete=models.CASCADE,
        verbose_name="Nəticə",
    )
    question_number = models.PositiveIntegerField(verbose_name="Sual nömrəsi")
    subject_name = models.CharField(max_length=255, verbose_name="Fənn adı")
    marker = models.ForeignKey(
        Marker, on_delete=models.SET_NULL,
        null=True, blank=True, verbose_name="Marker",
    )
    score = models.DecimalField(max_digits=10, decimal_places=3, default=0, verbose_name="Ball")
    notes = models.TextField(blank=True, default="", verbose_name="Qeydlər")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Marker cavab qiyməti (köhnə)"
        verbose_name_plural = "Marker cavab qiymətləri (köhnə)"
