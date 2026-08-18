from django.db import models


class ExamType(models.Model):
    exam_type_name = models.CharField(max_length=255, verbose_name="İmtahan tipi adı")
    subjects_with_counts = models.JSONField(
        default=list, blank=True,
        verbose_name="Fənlər və sual sayıları",
        help_text='[{"subject": "Riyaziyyat", "count": 30}, ...]',
    )
    pricing_config = models.JSONField(
        default=dict, blank=True,
        verbose_name="Qiymət konfiqurasiyası",
        help_text='{"course": 15, "other": 20}',
    )

    class Meta:
        verbose_name = "İmtahan tipi"
        verbose_name_plural = "İmtahan tipləri"

    def __str__(self):
        return self.exam_type_name


class Subject(models.Model):
    subject_name = models.CharField(max_length=255, verbose_name="Fənn adı")

    class Meta:
        verbose_name = "Fənn"
        verbose_name_plural = "Fənlər"

    def __str__(self):
        return self.subject_name


class Sinif(models.Model):
    sinif_name = models.CharField(max_length=100, verbose_name="Sinif adı")

    class Meta:
        verbose_name = "Sinif"
        verbose_name_plural = "Siniflər"

    def __str__(self):
        return self.sinif_name


class Bolme(models.Model):
    bolme_name = models.CharField(max_length=100, verbose_name="Bölmə adı")

    class Meta:
        verbose_name = "Bölmə"
        verbose_name_plural = "Bölmələr"

    def __str__(self):
        return self.bolme_name


class Qrup(models.Model):
    qrup_name = models.CharField(max_length=100, verbose_name="Qrup adı")

    class Meta:
        verbose_name = "Qrup"
        verbose_name_plural = "Qruplar"

    def __str__(self):
        return self.qrup_name


class District(models.Model):
    district_name = models.CharField(max_length=255, verbose_name="Rayon adı")

    class Meta:
        verbose_name = "Rayon"
        verbose_name_plural = "Rayonlar"

    def __str__(self):
        return self.district_name


class SchoolType(models.Model):
    school_type_name = models.CharField(max_length=255, verbose_name="Məktəb tipi")

    class Meta:
        verbose_name = "Məktəb tipi"
        verbose_name_plural = "Məktəb tipləri"

    def __str__(self):
        return self.school_type_name


class School(models.Model):
    school_name = models.CharField(max_length=255, verbose_name="Məktəb adı")
    district = models.ForeignKey(
        District, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="schools", verbose_name="Rayon",
    )
    school_type = models.ForeignKey(
        SchoolType, on_delete=models.SET_NULL, null=True, blank=True,
        verbose_name="Məktəb tipi",
    )

    class Meta:
        verbose_name = "Məktəb"
        verbose_name_plural = "Məktəblər"

    def __str__(self):
        return self.school_name


class Universities(models.Model):
    university_name = models.CharField(max_length=255, verbose_name="Universitet adı")

    class Meta:
        verbose_name = "Universitet"
        verbose_name_plural = "Universitetlər"

    def __str__(self):
        return self.university_name


class PreviousExam(models.Model):
    prev_exam_name = models.CharField(max_length=255, verbose_name="Əvvəlki imtahan adı")
    prev_exam_date = models.DateField(null=True, blank=True, verbose_name="Tarixi")
    prev_exam_price = models.DecimalField(
        max_digits=10, decimal_places=2, default=0,
        verbose_name="Qiyməti",
    )

    class Meta:
        verbose_name = "Əvvəlki imtahan"
        verbose_name_plural = "Əvvəlki imtahanlar"

    def __str__(self):
        return self.prev_exam_name
