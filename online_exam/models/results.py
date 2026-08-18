from django.db import models


class SagirdResult(models.Model):
    id = models.BigAutoField(primary_key=True)

    student_id = models.IntegerField(verbose_name="Qeydiyyat ID")
    exam_id = models.IntegerField(verbose_name="İmtahan ID")
    student_reg_number = models.CharField(
        max_length=10, verbose_name="İş nömrəsi",
    )
    attempt_number = models.PositiveIntegerField(default=1, verbose_name="Cəhd nömrəsi")

    first_name = models.CharField(max_length=100, blank=True, default="", verbose_name="Ad")
    last_name = models.CharField(max_length=100, blank=True, default="", verbose_name="Soyad")
    sinif = models.CharField(max_length=100, blank=True, default="", verbose_name="Sinif")
    variant = models.CharField(max_length=100, blank=True, default="", verbose_name="Variant")
    bolme = models.CharField(max_length=100, blank=True, default="", verbose_name="Bölmə")
    qrup = models.CharField(max_length=100, blank=True, default="", verbose_name="Qrup")

    session = models.OneToOneField(
        "online_exam.StudentExamSession", on_delete=models.SET_NULL,
        null=True, blank=True, verbose_name="Seans",
    )
    register = models.ForeignKey(
        "online_exam.Register", on_delete=models.SET_NULL,
        null=True, blank=True, verbose_name="Qeydiyyat",
    )
    cabinet = models.ForeignKey(
        "online_exam.StudentCabinet", on_delete=models.SET_NULL,
        null=True, blank=True, verbose_name="Kabinet",
    )

    result = models.JSONField(
        default=dict, blank=True,
        verbose_name="Nəticə (fənn → cavab stringi)",
        help_text='{"Riyaziyyat": "ABCDA..."}',
    )
    total_point = models.DecimalField(
        max_digits=10, decimal_places=2, default=0,
        verbose_name="Ümumi bal",
    )
    open_ended_scores = models.JSONField(
        default=dict, blank=True,
        verbose_name="Açıq sual balları",
    )
    result_details = models.JSONField(
        default=dict, blank=True,
        verbose_name="Nəticə detalları",
        help_text="""
        {
            "Riyaziyyat": {
                "point": 42.5,
                "correct": 8,
                "wrong": 2,
                "empty": 1,
                "open_ended_scores": {},
                "details": [
                    {
                        "question_number": 1,
                        "question_type": "Qapalı",
                        "is_open_ended": false,
                        "student_ans": "A",
                        "correct_ans": "A",
                        "result": "correct",
                        "earned_points": 5.0,
                        "raw_fraction": "1"
                    }
                ]
            }
        }
        """,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Şagird nəticəsi"
        verbose_name_plural = "Şagird nəticələri"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.last_name} {self.first_name} | exam={self.exam_id} | {self.total_point} bal"
