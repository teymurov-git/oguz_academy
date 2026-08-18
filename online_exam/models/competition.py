from django.db import models
from django.conf import settings


class Competition(models.Model):
    name = models.CharField(max_length=255, verbose_name="Müsabiqə adı")
    description = models.TextField(blank=True, default="", verbose_name="Təsvir")
    image = models.ImageField(
        upload_to="competitions/", null=True, blank=True, verbose_name="Şəkil",
    )
    start_datetime = models.DateTimeField(verbose_name="Başlama vaxtı")
    deadline = models.DateTimeField(verbose_name="Bitmə vaxtı")
    question_count = models.PositiveIntegerField(default=10, verbose_name="Sual sayı")
    is_active = models.BooleanField(default=True, verbose_name="Aktivdir?")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, verbose_name="Yaradan",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Müsabiqə"
        verbose_name_plural = "Müsabiqələr"

    def __str__(self):
        return self.name


class CompetitionQuestion(models.Model):
    class AnswerType(models.TextChoices):
        CLOSED = "qapalı", "Qapalı"
        OPEN = "açıq", "Açıq"
        MATCHING = "uyğunlaşdırma", "Uyğunlaşdırma"
        ESSAY = "esse", "Esse"

    class QuestionInputType(models.TextChoices):
        TEXT = "text", "Mətn"
        IMAGE = "image", "Şəkil"

    competition = models.ForeignKey(
        Competition, on_delete=models.CASCADE,
        related_name="questions", verbose_name="Müsabiqə",
    )
    start_datetime = models.DateTimeField(verbose_name="Sual başlama vaxtı")
    end_datetime = models.DateTimeField(verbose_name="Sual bitmə vaxtı")
    points = models.PositiveIntegerField(default=10, verbose_name="Ballar")
    duration_seconds = models.PositiveIntegerField(default=60, verbose_name="Müddət (saniyə)")
    order = models.PositiveIntegerField(default=0, verbose_name="Sıra")

    question_input_type = models.CharField(
        max_length=10, choices=QuestionInputType.choices,
        default=QuestionInputType.TEXT, verbose_name="Sual giriş tipi",
    )
    answer_type = models.CharField(
        max_length=20, choices=AnswerType.choices,
        default=AnswerType.CLOSED, verbose_name="Cavab tipi",
    )
    answer_options = models.JSONField(
        default=list, blank=True, verbose_name="Cavab seçimləri",
    )
    correct_answer = models.CharField(
        max_length=255, verbose_name="Düzgün cavab",
    )

    class Meta:
        verbose_name = "Müsabiqə sualı"
        verbose_name_plural = "Müsabiqə sualları"
        ordering = ["competition", "order"]

    def __str__(self):
        return f"{self.competition} — Q{self.order}"


class CompetitionParticipant(models.Model):
    competition = models.ForeignKey(
        Competition, on_delete=models.CASCADE,
        related_name="participants", verbose_name="Müsabiqə",
    )
    student = models.ForeignKey(
        "online_exam.StudentCabinet", on_delete=models.CASCADE,
        related_name="competitions", verbose_name="Şagird",
    )
    total_score = models.DecimalField(
        max_digits=10, decimal_places=2, default=0,
        verbose_name="Ümumi bal",
    )
    total_answer_time_ms = models.PositiveIntegerField(
        default=0, verbose_name="Ümumi cavab vaxtı (ms)",
    )
    joined_at = models.DateTimeField(auto_now_add=True, verbose_name="Qoşulma vaxtı")

    class Meta:
        verbose_name = "Müsabiqə iştirakçısı"
        verbose_name_plural = "Müsabiqə iştirakçıları"
        unique_together = ["competition", "student"]

    def __str__(self):
        return f"{self.student} → {self.competition}"


class CompetitionQuestionAttempt(models.Model):
    participant = models.ForeignKey(
        CompetitionParticipant, on_delete=models.CASCADE,
        related_name="attempts", verbose_name="İştirakçı",
    )
    question = models.ForeignKey(
        CompetitionQuestion, on_delete=models.CASCADE,
        related_name="attempts", verbose_name="Sual",
    )
    started_at = models.DateTimeField(auto_now_add=True, verbose_name="Başlama")
    submitted_at_ms = models.PositiveIntegerField(
        null=True, blank=True, verbose_name="Təqdim (ms)",
    )
    answer = models.CharField(max_length=255, blank=True, default="", verbose_name="Cavab")
    is_correct = models.BooleanField(default=False, verbose_name="Düzgündür?")
    points_earned = models.DecimalField(
        max_digits=10, decimal_places=2, default=0,
        verbose_name="Qazanılan ballar",
    )
    is_timeout = models.BooleanField(default=False, verbose_name="Vaxt bitdi?")

    class Meta:
        verbose_name = "Müsabiqə cavabı"
        verbose_name_plural = "Müsabiqə cavabları"
        unique_together = ["participant", "question"]

    def __str__(self):
        return f"{self.participant} — Q{self.question.order}"
