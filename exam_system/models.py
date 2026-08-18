import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone


class ExamType(models.TextChoices):
    ABITURIENT = 'abiturient', 'Abituriyent'
    ENTRANCE = 'entrance', 'Qəbul imtahanı'
    PLACEMENT = 'placement', 'Yerləşdirmə imtahanı'
    COURSE = 'course', 'Kurs imtahanı'
    COMPETITION = 'competition', 'Sınaq/Südüş'


class ExamStatus(models.TextChoices):
    DRAFT = 'draft', 'Qaralama'
    PUBLISHED = 'published', 'Dərc olunmuş'
    ACTIVE = 'active', 'Aktiv'
    COMPLETED = 'completed', 'Bitmiş'
    ARCHIVED = 'archived', 'Arxivlənmiş'


class QuestionType(models.TextChoices):
    SINGLE_CHOICE = 'single_choice', 'Tək seçimli'
    MULTIPLE_CHOICE = 'multiple_choice', 'Çox seçimli'
    TRUE_FALSE = 'true_false', 'Doğru/Yanlış'
    TEXT = 'text', 'Mətn'
    MATCHING = 'matching', 'Uyğunluq'
    ORDERING = 'ordering', 'Sıralama'


class DifficultyLevel(models.IntegerChoices):
    EASY = 1, 'Asan'
    MEDIUM = 2, 'Orta'
    HARD = 3, 'Çətin'
    EXPERT = 4, 'Ekspert'


class Exam(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField('Başlıq', max_length=300)
    slug = models.SlugField(max_length=300, unique=True, blank=True)
    description = models.TextField('Təsvir', blank=True)
    exam_type = models.CharField('İmtahan növü', max_length=20, choices=ExamType.choices)
    status = models.CharField('Status', max_length=20, choices=ExamStatus.choices, default=ExamStatus.DRAFT)

    dim_type = models.CharField('DİM növü', max_length=20, blank=True, choices=(
        ('buraxilis', 'Buraxılış'),
        ('blok', 'Blok'),
    ), help_text='DİM bal sistemi ilə hesablanan imtahanlar üçün')
    exam_group = models.CharField('Qrup', max_length=2, blank=True, choices=(
        ('1', 'I qrup'), ('2', 'II qrup'), ('3', 'III qrup'), ('4', 'IV qrup'),
    ))
    group_subtype = models.CharField('Alt növ', max_length=10, blank=True, choices=(
        ('', 'Standart'),
        ('ri', 'Rİ'),
        ('rk', 'RK'),
        ('tc', 'TC'),
        ('dt', 'DT'),
    ))

    subject = models.CharField('Fənn', max_length=200, blank=True)
    total_questions = models.IntegerField('Ümumi sual sayı', default=0)
    total_time_minutes = models.IntegerField('Müddət (dəqiqə)', default=0)
    passing_score = models.DecimalField('Keçid balı', max_digits=5, decimal_places=2, default=0)
    max_score = models.DecimalField('Maksimum bal', max_digits=10, decimal_places=2, default=100)

    course = models.ForeignKey('courses.Course', on_delete=models.SET_NULL, null=True, blank=True, related_name='system_exams', verbose_name='Kurs')
    group = models.ForeignKey('courses.Group', on_delete=models.SET_NULL, null=True, blank=True, related_name='system_exams', verbose_name='Qrup')

    start_datetime = models.DateTimeField('Başlama tarixi', null=True, blank=True)
    end_datetime = models.DateTimeField('Bitmə tarixi', null=True, blank=True)
    registration_deadline = models.DateTimeField('Qeydiyyat son tarixi', null=True, blank=True)

    price = models.DecimalField('Qiymət', max_digits=10, decimal_places=2, default=0)
    max_participants = models.IntegerField('Maksimum iştirakçı', default=0)
    location = models.CharField('Məkan', max_length=200, blank=True)

    allow_variant_selection = models.BooleanField('Variant seçiminə icazə', default=True)
    shuffle_questions = models.BooleanField('Sualları qarışdır', default=True)
    shuffle_options = models.BooleanField('Seçimləri qarışdır', default=True)
    show_results_immediately = models.BooleanField('Nəticələri dərhal göstər', default=False)
    allow_review = models.BooleanField('Baxışa icazə', default=True)

    is_active = models.BooleanField('Aktiv', default=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_exams', verbose_name='Yaradan')
    created_at = models.DateTimeField('Yaradılma tarixi', auto_now_add=True)
    updated_at = models.DateTimeField('Yenilənmə tarixi', auto_now=True)

    class Meta:
        ordering = ('-created_at',)
        verbose_name = 'İmtahan'
        verbose_name_plural = 'İmtahanlar'

    def __str__(self):
        return self.title

    @property
    def registered_count(self):
        return self.student_exams.count()

    @property
    def is_registration_open(self):
        if self.registration_deadline:
            return timezone.now() < self.registration_deadline
        return self.status == ExamStatus.PUBLISHED

    @property
    def is_active_now(self):
        now = timezone.now()
        if self.start_datetime and self.end_datetime:
            return self.start_datetime <= now <= self.end_datetime
        return self.status == ExamStatus.ACTIVE


class Question(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='questions', verbose_name='İmtahan')
    question_type = models.CharField('Sual növü', max_length=20, choices=QuestionType.choices)
    text = models.TextField('Sual mətni')
    image = models.ImageField('Şəkil', upload_to='exam_questions/', null=True, blank=True)

    answers_data = models.JSONField('Cavablar (JSON)', default=dict, blank=True,
        help_text='JSON formatında cavab variantları. Nümunə: {"options": [{"id": "a", "text": "...", "is_correct": true}, ...], "correct_text": "..."}')

    subject = models.CharField('Fənn', max_length=200, blank=True)
    question_number = models.IntegerField('Sual nömrəsi', null=True, blank=True)

    difficulty = models.IntegerField('Çətinlik', choices=DifficultyLevel.choices, default=DifficultyLevel.MEDIUM)
    points = models.DecimalField('Ball', max_digits=5, decimal_places=2, default=1)
    sort_order = models.IntegerField('Sıralama', default=0)
    explanation = models.TextField('Açıqlama', blank=True)

    is_active = models.BooleanField('Aktiv', default=True)
    created_at = models.DateTimeField('Yaradılma tarixi', auto_now_add=True)
    updated_at = models.DateTimeField('Yenilənmə tarixi', auto_now=True)

    class Meta:
        ordering = ('sort_order', 'created_at')
        verbose_name = 'Sual'
        verbose_name_plural = 'Suallar'

    def __str__(self):
        return f"{self.text[:80]}... ({self.get_question_type_display()})"


class Variant(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='variants', verbose_name='İmtahan')
    name = models.CharField('Ad', max_length=100)
    code = models.CharField('Kod', max_length=50)
    description = models.TextField('Təsvir', blank=True)

    questions = models.ManyToManyField(Question, related_name='variants', verbose_name='Suallar', blank=True)

    sort_order = models.IntegerField('Sıralama', default=0)
    is_active = models.BooleanField('Aktiv', default=True)
    created_at = models.DateTimeField('Yaradılma tarixi', auto_now_add=True)

    class Meta:
        ordering = ('sort_order', 'name')
        verbose_name = 'Variant'
        verbose_name_plural = 'Variantlar'
        unique_together = ('exam', 'code')

    def __str__(self):
        return f"{self.exam.title} — {self.name}"


class StudentExam(models.Model):
    STATUS_CHOICES = [
        ('registered', 'Qeydiyyatdan keçib'),
        ('in_progress', 'Davam edir'),
        ('completed', 'Bitirib'),
        ('cancelled', 'Ləğv olunub'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='student_exams', verbose_name='İmtahan')
    student = models.ForeignKey('students.Student', on_delete=models.CASCADE, related_name='student_exams', verbose_name='Tələbə')
    variant = models.ForeignKey(Variant, on_delete=models.SET_NULL, null=True, blank=True, related_name='student_exams', verbose_name='Variant')

    status = models.CharField('Status', max_length=20, choices=STATUS_CHOICES, default='registered')
    score = models.DecimalField('Bal', max_digits=10, decimal_places=2, null=True, blank=True)
    percentage = models.DecimalField('Faiz', max_digits=5, decimal_places=2, null=True, blank=True)
    passed = models.BooleanField('Keçib', null=True, blank=True)

    dim_result = models.JSONField('DİM nəticəsi', default=dict, blank=True)
    dim_total_bal = models.DecimalField('DİM ümumi bal', max_digits=8, decimal_places=1, null=True, blank=True)
    dim_max_bal = models.DecimalField('DİM maksimal bal', max_digits=8, decimal_places=1, null=True, blank=True)

    started_at = models.DateTimeField('Başlama vaxtı', null=True, blank=True)
    completed_at = models.DateTimeField('Bitirmə vaxtı', null=True, blank=True)
    time_spent_seconds = models.IntegerField('Xərclənən vaxt (saniyə)', default=0)

    ip_address = models.GenericIPAddressField('IP ünvanı', null=True, blank=True)
    user_agent = models.TextField('Brauzer məlumatı', blank=True)

    created_at = models.DateTimeField('Yaradılma tarixi', auto_now_add=True)
    updated_at = models.DateTimeField('Yenilənmə tarixi', auto_now=True)

    class Meta:
        ordering = ('-created_at',)
        verbose_name = 'Tələbə imtahanı'
        verbose_name_plural = 'Tələbə imtahanları'
        unique_together = ('exam', 'student')

    def __str__(self):
        return f"{self.student} — {self.exam.title}"


class StudentAnswer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student_exam = models.ForeignKey(StudentExam, on_delete=models.CASCADE, related_name='answers', verbose_name='İmtahan')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='student_answers', verbose_name='Sual')

    selected_option_ids = models.JSONField('Seçilmiş cavablar', default=list, blank=True)
    text_answer = models.TextField('Mətn cavabı', blank=True)
    matching_data = models.JSONField('Uyğunluq məlumatı', default=dict, blank=True)
    ordering_data = models.JSONField('Sıralama məlumatı', default=list, blank=True)

    is_correct = models.BooleanField('Doğrudur', null=True, blank=True)
    points_earned = models.DecimalField('Qazanılan bal', max_digits=5, decimal_places=2, default=0)

    answered_at = models.DateTimeField('Cavablandırma vaxtı', auto_now_add=True)

    class Meta:
        ordering = ('answered_at',)
        verbose_name = 'Tələbə cavabı'
        verbose_name_plural = 'Tələbə cavabları'
        unique_together = ('student_exam', 'question')

    def __str__(self):
        return f"{self.student_exam} — {self.question}"


class MarkerConsensus(models.Model):
    """
    Marker konsensus sistemi — rəy müxtəlifliyi olduqda 3 marker qiymətləndirir.
    Qayda: 0/1/3/1/2/3/1 — hər markerin balları cəmlənib orta hesablanır.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student_answer = models.ForeignKey(StudentAnswer, on_delete=models.CASCADE, related_name='marker_consensus', verbose_name='Tələbə cavabı')

    marker1_score = models.DecimalField('Marker 1 balı', max_digits=5, decimal_places=2, null=True, blank=True)
    marker1_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='marker1_consensus', verbose_name='Marker 1')
    marker1_notes = models.TextField('Marker 1 qeydləri', blank=True)

    marker2_score = models.DecimalField('Marker 2 balı', max_digits=5, decimal_places=2, null=True, blank=True)
    marker2_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='marker2_consensus', verbose_name='Marker 2')
    marker2_notes = models.TextField('Marker 2 qeydləri', blank=True)

    marker3_score = models.DecimalField('Marker 3 balı', max_digits=5, decimal_places=2, null=True, blank=True)
    marker3_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='marker3_consensus', verbose_name='Marker 3')
    marker3_notes = models.TextField('Marker 3 qeydləri', blank=True)

    final_score = models.DecimalField('Yekun bal', max_digits=5, decimal_places=2, null=True, blank=True)
    is_resolved = models.BooleanField('Həll olunub', default=False)

    created_at = models.DateTimeField('Yaradılma tarixi', auto_now_add=True)
    updated_at = models.DateTimeField('Yenilənmə tarixi', auto_now=True)

    class Meta:
        verbose_name = 'Marker konsensusu'
        verbose_name_plural = 'Marker konsensusları'

    def __str__(self):
        return f"Consensus — {self.student_answer}"

    def calculate_final_score(self):
        scores = [s for s in [self.marker1_score, self.marker2_score, self.marker3_score] if s is not None]
        if scores:
            self.final_score = sum(scores) / len(scores)
            self.is_resolved = True
            self.save()
            return self.final_score
        return None


class Competition(models.Model):
    """Sınaq imtahanı — bir neçə imtahanın birləşdirilməsi"""
    STATUS_CHOICES = [
        ('draft', 'Qaralama'),
        ('active', 'Aktiv'),
        ('completed', 'Bitmiş'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField('Başlıq', max_length=300)
    slug = models.SlugField(max_length=300, unique=True, blank=True)
    description = models.TextField('Təsvir', blank=True)
    status = models.CharField('Status', max_length=20, choices=STATUS_CHOICES, default='draft')

    exams = models.ManyToManyField(Exam, related_name='competitions', verbose_name='İmtahanlar', blank=True)

    start_datetime = models.DateTimeField('Başlama tarixi', null=True, blank=True)
    end_datetime = models.DateTimeField('Bitmə tarixi', null=True, blank=True)

    is_active = models.BooleanField('Aktiv', default=True)
    created_at = models.DateTimeField('Yaradılma tarixi', auto_now_add=True)
    updated_at = models.DateTimeField('Yenilənmə tarixi', auto_now=True)

    class Meta:
        ordering = ('-created_at',)
        verbose_name = 'Sınaq/Südüş'
        verbose_name_plural = 'Sınaqlar/Südüşlər'

    def __str__(self):
        return self.title
