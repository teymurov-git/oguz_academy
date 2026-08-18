import uuid
from django.db import models
from django.utils.text import slugify


class AcademicYear(models.Model):
    name = models.CharField('Ad', max_length=20, unique=True)
    start_date = models.DateField('Başlama tarixi')
    end_date = models.DateField('Bitmə tarixi')
    is_current = models.BooleanField('Cari il', default=False)

    class Meta:
        ordering = ('-start_date',)
        verbose_name = 'Tədris ili'
        verbose_name_plural = 'Tədris illəri'

    def save(self, *args, **kwargs):
        if self.is_current:
            AcademicYear.objects.filter(is_current=True).update(is_current=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class CourseCategory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField('Ad', max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    description = models.TextField('Təsvir', blank=True)
    icon = models.CharField('İkon', max_length=100, blank=True)
    sort_order = models.IntegerField('Sıralama', default=0)
    is_active = models.BooleanField('Aktiv', default=True)

    class Meta:
        ordering = ('sort_order', 'name')
        verbose_name = 'Kurs kateqoriyası'
        verbose_name_plural = 'Kurs kateqoriyaları'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Course(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    category = models.ForeignKey(CourseCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='courses', verbose_name='Kateqoriya')
    name = models.CharField('Ad', max_length=300)
    slug = models.SlugField(max_length=300, unique=True, blank=True)
    description = models.TextField('Təsvir', blank=True)
    thumbnail = models.ImageField('Şəkil', upload_to='courses/', null=True, blank=True)
    teacher = models.ForeignKey('teachers.Teacher', on_delete=models.SET_NULL, null=True, blank=True, related_name='courses', verbose_name='Müəllim')
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.SET_NULL, null=True, blank=True, related_name='courses', verbose_name='Tədris ili')
    duration_weeks = models.IntegerField('Müddət (həftə)', default=0)
    lesson_count = models.IntegerField('Dərs sayı', default=0)
    price = models.DecimalField('Qiymət', max_digits=10, decimal_places=2, default=0)
    installment_allowed = models.BooleanField('Hissə-hissə ödəniş', default=True)
    max_installments = models.IntegerField('Maksimum hissə', default=0)
    curriculum = models.JSONField('Tədris proqramı', default=list, blank=True)
    requirements = models.JSONField('Tələblər', default=list, blank=True)
    is_active = models.BooleanField('Aktiv', default=True)
    created_at = models.DateTimeField('Yaradılma tarixi', auto_now_add=True)
    updated_at = models.DateTimeField('Yenilənmə tarixi', auto_now=True)

    class Meta:
        ordering = ('name',)
        verbose_name = 'Kurs'
        verbose_name_plural = 'Kurslar'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Group(models.Model):
    WEEKDAY_CHOICES = [
        ('monday', 'Bazar ertəsi'),
        ('tuesday', 'Çərşənbə axşamı'),
        ('wednesday', 'Çərşənbə'),
        ('thursday', 'Cümə axşamı'),
        ('friday', 'Cümə'),
        ('saturday', 'Şənbə'),
        ('sunday', 'Bazar'),
    ]
    TYPE_CHOICES = [
        ('group', 'Qrup'),
        ('individual', 'Fərdi'),
        ('intensive', 'İntensiv'),
    ]
    STATUS_CHOICES = [
        ('active', 'Aktiv'),
        ('completed', 'Bitmiş'),
        ('cancelled', 'Ləğv olunmuş'),
        ('pending', 'Gözləyir'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField('Ad', max_length=200)
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True, related_name='groups', verbose_name='Kurs')
    teacher = models.ForeignKey('teachers.Teacher', on_delete=models.SET_NULL, null=True, blank=True, related_name='groups', verbose_name='Müəllim')
    students = models.ManyToManyField('students.Student', through='courses.GroupStudent', related_name='groups', verbose_name='Tələbələr')
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.SET_NULL, null=True, blank=True, related_name='groups', verbose_name='Tədris ili')
    type = models.CharField('Tip', max_length=20, choices=TYPE_CHOICES, default='group')
    schedule_text = models.CharField('Cədvəl', max_length=200, blank=True)
    weekdays = models.JSONField('Həftənin günləri', default=list, blank=True, help_text='Seçilmiş günlər')
    start_date = models.DateField('Başlama tarixi', null=True, blank=True)
    end_date = models.DateField('Bitmə tarixi', null=True, blank=True)
    max_students = models.IntegerField('Maksimum tələbə', default=20)
    price = models.DecimalField('Qiymət', max_digits=10, decimal_places=2, null=True, blank=True)
    status = models.CharField('Status', max_length=20, choices=STATUS_CHOICES, default='active')
    is_active = models.BooleanField('Aktiv', default=True)
    created_at = models.DateTimeField('Yaradılma tarixi', auto_now_add=True)
    updated_at = models.DateTimeField('Yenilənmə tarixi', auto_now=True)

    class Meta:
        ordering = ('-created_at',)
        verbose_name = 'Qrup'
        verbose_name_plural = 'Qruplar'

    def __str__(self):
        if self.course:
            return f"{self.name} - {self.course.name}"
        return self.name


class Exam(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField('Başlıq', max_length=300)
    slug = models.SlugField(max_length=300, unique=True, blank=True)
    description = models.TextField('Təsvir', blank=True)
    date = models.DateTimeField('Tarix')
    registration_deadline = models.DateTimeField('Qeydiyyat son tarixi')
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.SET_NULL, null=True, blank=True, related_name='exams', verbose_name='Tədris ili')
    price = models.DecimalField('Qiymət', max_digits=10, decimal_places=2, default=0)
    max_participants = models.IntegerField('Maksimum iştirakçı', default=0)
    location = models.CharField('Məkan', max_length=200, blank=True)
    is_active = models.BooleanField('Aktiv', default=True)
    created_at = models.DateTimeField('Yaradılma tarixi', auto_now_add=True)

    class Meta:
        ordering = ('-date',)
        verbose_name = 'Sınaq imtahanı'
        verbose_name_plural = 'Sınaq imtahanları'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class ExamRegistration(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='registrations', verbose_name='İmtahan')
    first_name = models.CharField('Ad', max_length=150)
    last_name = models.CharField('Soyad', max_length=150)
    email = models.EmailField('Email')
    phone = models.CharField('Telefon', max_length=50)
    message = models.TextField('Mesaj', blank=True)
    registered_at = models.DateTimeField('Qeydiyyat tarixi', auto_now_add=True)

    class Meta:
        ordering = ('-registered_at',)
        verbose_name = 'İmtahan qeydiyyatı'
        verbose_name_plural = 'İmtahan qeydiyyatları'

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.exam.title}"


class GroupStudent(models.Model):
    STATUS_CHOICES = [
        ('active', 'Aktiv'),
        ('frozen', 'Dondurulmuş'),
        ('dropped', 'Ayrılıb'),
        ('completed', 'Bitirib'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='group_students', verbose_name='Qrup')
    student = models.ForeignKey('students.Student', on_delete=models.CASCADE, related_name='group_students', verbose_name='Tələbə')
    status = models.CharField('Status', max_length=20, choices=STATUS_CHOICES, default='active')
    joined_at = models.DateTimeField('Qoşulma tarixi', auto_now_add=True)
    left_at = models.DateTimeField('Ayrılma tarixi', null=True, blank=True)

    class Meta:
        unique_together = ('group', 'student')
        verbose_name = 'Qrup tələbəsi'
        verbose_name_plural = 'Qrup tələbələri'

    def __str__(self):
        return f"{self.student} - {self.group}"
