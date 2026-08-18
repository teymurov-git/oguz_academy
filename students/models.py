import uuid
from django.db import models
from django.conf import settings


class Student(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('none', 'Məlumat yoxdur'),
        ('pending', 'Gözləyir'),
        ('up_to_date', 'Borcu yoxdur'),
        ('overdue', 'Gecikmiş'),
    ]

    STATUS_CHOICES = [
        ('active', 'Aktiv'),
        ('frozen', 'Dondurulmuş'),
        ('graduated', 'Məzun'),
        ('transferred', 'Köçürülmüş'),
        ('dropped', 'Ayrılıb'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='student_profile', verbose_name='İstifadəçi')
    student_id = models.CharField('Tələbə ID', max_length=50, unique=True, blank=True)
    work_number = models.PositiveIntegerField('İş nömrəsi', unique=True, null=True, blank=True,
        help_text='Nəticə axtarışı üçün 5 rəqəmli iş nömrəsi. Avtomatik yaradılır.')
    parent = models.ForeignKey('students.Parent', on_delete=models.SET_NULL, null=True, blank=True, related_name='children', verbose_name='Valideyn')
    parent_phone = models.CharField('Valideyn telefonu', max_length=50, blank=True)
    date_of_birth = models.DateField('Doğum tarixi', null=True, blank=True)
    gender = models.CharField('Cins', max_length=10, choices=[('male', 'Kişi'), ('female', 'Qadın')], blank=True)
    address = models.TextField('Ünvan', blank=True)
    phone = models.CharField('Telefon', max_length=50, blank=True)
    emergency_phone = models.CharField('Təcili telefon', max_length=50, blank=True)
    school = models.CharField('Məktəb', max_length=200, blank=True)
    grade_level = models.CharField('Sinif', max_length=20, blank=True)
    status = models.CharField('Status', max_length=20, choices=STATUS_CHOICES, default='active')
    enrollment_date = models.DateField('Qeydiyyat tarixi', null=True, blank=True)
    notes = models.TextField('Qeydlər', blank=True)
    is_active = models.BooleanField('Aktiv', default=True)
    monthly_payment = models.DecimalField('Aylıq ödəniş', max_digits=10, decimal_places=2, null=True, blank=True)
    discount = models.DecimalField('Endirim (AZN)', max_digits=10, decimal_places=2, default=0)
    last_payment_date = models.DateField('Son ödəniş tarixi', null=True, blank=True)
    payment_status = models.CharField('Ödəniş statusu', max_length=20, choices=PAYMENT_STATUS_CHOICES, default='none')
    teachers = models.ManyToManyField('teachers.Teacher', blank=True, related_name='students', verbose_name='Müəllimlər')
    academic_year = models.ForeignKey('courses.AcademicYear', on_delete=models.SET_NULL, null=True, blank=True, related_name='students', verbose_name='Tədris ili')
    created_at = models.DateTimeField('Yaradılma tarixi', auto_now_add=True)
    updated_at = models.DateTimeField('Yenilənmə tarixi', auto_now=True)

    class Meta:
        ordering = ('-created_at',)
        verbose_name = 'Tələbə'
        verbose_name_plural = 'Tələbələr'

    def save(self, *args, **kwargs):
        if not self.student_id:
            self.student_id = self._generate_student_id()
        if not self.work_number:
            self.work_number = self._generate_work_number()
        super().save(*args, **kwargs)

    @classmethod
    def _generate_student_id(cls):
        import random
        used = set(cls.objects.exclude(student_id=None).values_list('student_id', flat=True))
        used |= {str(w) for w in cls.objects.exclude(work_number=None).values_list('work_number', flat=True)}
        for _ in range(100):
            number = random.randint(10000, 99999)
            if str(number) not in used:
                return str(number)
        candidate = 10000
        while str(candidate) in used:
            candidate += 1
        return str(candidate)

    @staticmethod
    def _generate_work_number():
        import random
        for _ in range(50):
            number = random.randint(10000, 99999)
            if not Student.objects.filter(work_number=number).exists():
                return number
        return Student.objects.aggregate(models.Max('work_number'))['work_number__max'] or 10000 + 1

    def __str__(self):
        return self.user.get_full_name() or self.user.username


class Parent(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='parent_profile', verbose_name='İstifadəçi')
    phone = models.CharField('Telefon', max_length=50)
    occupation = models.CharField('Peşə', max_length=200, blank=True)
    address = models.TextField('Ünvan', blank=True)
    is_primary = models.BooleanField('Əsas əlaqə', default=True)
    notes = models.TextField('Qeydlər', blank=True)
    created_at = models.DateTimeField('Yaradılma tarixi', auto_now_add=True)

    class Meta:
        verbose_name = 'Valideyn'
        verbose_name_plural = 'Valideynlər'

    def __str__(self):
        return self.user.get_full_name() or self.user.username
