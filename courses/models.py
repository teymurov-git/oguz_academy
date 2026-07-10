from django.db import models
from django.utils.text import slugify


class Exam(models.Model):
    title = models.CharField('title', max_length=200)
    slug = models.SlugField('slug', unique=True, blank=True)
    description = models.TextField('description')
    date = models.DateTimeField('exam date')
    registration_deadline = models.DateTimeField('registration deadline', null=True, blank=True)
    is_active = models.BooleanField('active', default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-date',)
        verbose_name = 'Exam'
        verbose_name_plural = 'Exams'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class ExamRegistration(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='registrations')
    first_name = models.CharField('first name', max_length=100)
    last_name = models.CharField('last name', max_length=100)
    email = models.EmailField('email')
    phone = models.CharField('phone', max_length=50)
    message = models.TextField('message', blank=True)
    registered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Registration'
        verbose_name_plural = 'Registrations'

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.exam.title}"


class Course(models.Model):
    name = models.CharField('name', max_length=200)
    description = models.TextField('description', blank=True)
    price = models.DecimalField('price', max_digits=10, decimal_places=2)
    duration_weeks = models.PositiveIntegerField('duration (weeks)')
    is_active = models.BooleanField('active', default=True)

    class Meta:
        verbose_name = 'Course'
        verbose_name_plural = 'Courses'

    def __str__(self):
        return self.name


class Group(models.Model):
    name = models.CharField('name', max_length=200)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='groups')
    teacher = models.ForeignKey('teachers.Teacher', on_delete=models.SET_NULL, null=True, blank=True, related_name='groups')
    students = models.ManyToManyField('students.Student', related_name='groups', blank=True)
    schedule = models.CharField('schedule', max_length=200)
    start_date = models.DateField('start date')
    end_date = models.DateField('end date', null=True, blank=True)
    max_students = models.PositiveIntegerField('max students', default=20)
    is_active = models.BooleanField('active', default=True)

    class Meta:
        verbose_name = 'Group'
        verbose_name_plural = 'Groups'

    def __str__(self):
        return f"{self.name} - {self.course.name}"
