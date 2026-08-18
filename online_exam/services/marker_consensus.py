"""
Bölmə 7: Marker Konsensus Qiymətləndirmə Sistemi

Blind grading, fraksiya əsaslı, çox-marker konsensus.
"""
from decimal import Decimal
from django.db import transaction
from django.utils import timezone

from ..models.markers import (
    Marker, QuestionAssignment, StudentAnswerGrading, IndividualGrade,
)
from ..models.results import SagirdResult
from ..models.cabinet import StudentAnswer, StudentExamSession
from .scoring import FRACTION_MAP, _round_score, _is_open_ended, _is_trivial_answer


def _check_consensus(grading: StudentAnswerGrading) -> str | None:
    """
    Konsensusu yoxla: 2+ eyni fraksiya → konsensus fraksiyası.
    Eyni fraksiya yoxdursa None qaytarır.
    """
    grades = grading.individual_grades.all()
    if grades.count() < 2:
        return None

    fraction_counts: dict[str, int] = {}
    for g in grades:
        f = g.fraction.strip()
        fraction_counts[f] = fraction_counts.get(f, 0) + 1

    for frac, count in fraction_counts.items():
        if count >= 2:
            return frac

    return None


def _apply_score_to_result(
    grading: StudentAnswerGrading,
    fraction_str: str,
    max_points: float,
):
    """
    Qiyməti SagirdResult.result_details-a tətbiq et.
    Fraksiya → earned_points hesabla, result_details-ı yenilə,
    fənn balını və total_point-i yenidən hesabla.
    """
    result = grading.result
    if not result or not result.result_details:
        return

    details = result.result_details
    subject = grading.subject_name
    q_num = grading.question_number

    if subject not in details:
        return

    subject_details = details[subject]
    detail_list = subject_details.get("details", [])

    frac_dec = _fraction_to_decimal(fraction_str)
    max_dec = Decimal(str(max_points))
    earned = _round_score(frac_dec * max_dec, 3)

    for d in detail_list:
        if d.get("question_number") == q_num:
            d["result"] = "open_ended_scored"
            d["earned_points"] = float(earned)
            d["raw_fraction"] = fraction_str
            break

    # Fənn balını yenidən hesabla
    total_subject = Decimal("0")
    correct_count = 0
    wrong_count = 0
    empty_count = 0
    for d in detail_list:
        ep = Decimal(str(d.get("earned_points", 0)))
        total_subject += ep
        r = d.get("result", "empty")
        if r == "correct":
            correct_count += 1
        elif r == "wrong":
            wrong_count += 1
        elif r == "empty" or "open_ended" in r:
            empty_count += 1

    subject_details["point"] = float(_round_score(total_subject, 4))
    subject_details["correct"] = correct_count
    subject_details["wrong"] = wrong_count
    subject_details["empty"] = empty_count

    details[subject] = subject_details
    result.result_details = details

    # total_point yenidən hesabla
    grand_total = Decimal("0")
    for subj_name, subj_data in details.items():
        grand_total += Decimal(str(subj_data.get("point", 0)))
    result.total_point = float(_round_score(grand_total, 2))

    result.save(update_fields=["result_details", "total_point", "updated_at"])


def _finalize_grading(
    grading: StudentAnswerGrading,
    fraction_str: str,
    numeric_score: float,
    max_points: float,
    is_head_marker_override: bool = False,
):
    """Qiymətləndirməni tamamla (finalize)."""
    grading.status = StudentAnswerGrading.Status.FINALIZED
    grading.final_fraction = fraction_str
    grading.final_score = numeric_score
    grading.save(update_fields=["status", "final_score", "final_fraction", "updated_at"])

    _apply_score_to_result(grading, fraction_str, max_points)


@transaction.atomic
def submit_grade(
    grading: StudentAnswerGrading,
    marker: Marker,
    fraction_str: str,
    max_points: float,
    is_suspicious: bool = False,
    notes: str = "",
) -> dict:
    """
    Marker tərəfindən bir qiymət təqdim olunur.
    Konsensus məntiqi ilə qərar qəbul edilir.

    Qərar ağacı (spesifikasiya Bölmə 7.3):
    1. Şübhəli → head_marker statusuna
    2. Baş Marker override → dərhal finalize
    3. Tək marker (N=1) → dərhal finalize
    4. Çox-marker konsensus (N≥2):
       - 2+ eyni fraksiya → finalize
       - Konsensus yoxdur + qalan marker var → in_progress, növbəti markerə
       - Konsensus yoxdur + hamı qiymətləndirib → head_marker statusuna
    5. Finalize → SagirdResult yenilə

    Returns:
        {"action": str, "status": str, "detail": str}
    """
    grading = StudentAnswerGrading.objects.select_for_update().get(pk=grading.pk)

    if grading.status == StudentAnswerGrading.Status.FINALIZED:
        return {"action": "already_finalized", "status": grading.status}

    # Fraksiyanı normallaşdır
    fraction_str = fraction_str.strip()
    if fraction_str not in FRACTION_MAP:
        return {"action": "error", "detail": f"Etibarsız fraksiya: {fraction_str}"}

    numeric_score = float(_round_score(
        _fraction_to_decimal(fraction_str) * Decimal(str(max_points)), 3
    ))

    # Fərdi qiymət yarat
    individual, created = IndividualGrade.objects.update_or_create(
        answer_grading=grading,
        marker=marker,
        defaults={
            "fraction": fraction_str,
            "numeric_score": numeric_score,
            "max_points": max_points,
            "is_suspicious": is_suspicious,
            "notes": notes,
        },
    )

    # 1. Şübhəli bayrağı → dərhal Baş Markerə
    if is_suspicious:
        grading.status = StudentAnswerGrading.Status.HEAD_MARKER
        grading.is_suspicious = True
        grading.save(update_fields=["status", "is_suspicious", "updated_at"])
        return {
            "action": "flagged_suspicious",
            "status": grading.status,
            "detail": "Şübhəli kimi işarələndi, Baş Markerə göndərildi",
        }

    # 2. Baş Marker override → dərhal finalize
    if marker.is_head_marker:
        _finalize_grading(grading, fraction_str, numeric_score, max_points, is_head_marker_override=True)
        individual.is_head_marker_override = True
        individual.save(update_fields=["is_head_marker_override"])
        return {
            "action": "head_marker_override",
            "status": grading.status,
            "detail": "Baş Marker tərəfindən dərhal tamamlandı",
        }

    assignment = grading.assignment
    required_count = assignment.required_marker_count

    # 3. Tək marker (N=1)
    if required_count <= 1:
        _finalize_grading(grading, fraction_str, numeric_score, max_points)
        return {
            "action": "finalized_single_marker",
            "status": grading.status,
            "detail": "Tək marker ilə tamamlandı",
        }

    # 4. Çox-marker konsensus (N≥2)
    all_grades = grading.individual_grades.all()
    graded_count = all_grades.count()

    # Konsensusu yoxla
    consensus_fraction = _check_consensus(grading)

    if consensus_fraction:
        # Konsensus tapıldı
        consensus_numeric = float(_round_score(
            _fraction_to_decimal(consensus_fraction) * Decimal(str(max_points)), 3
        ))
        _finalize_grading(grading, consensus_fraction, consensus_numeric, max_points)
        return {
            "action": "consensus_reached",
            "status": grading.status,
            "detail": f"Konsensus fraksiyası: {consensus_fraction}",
        }

    # Konsensus yoxdur
    if graded_count < required_count:
        # Qalan markerlər var → davam et
        grading.status = StudentAnswerGrading.Status.IN_PROGRESS
        grading.current_marker_index = graded_count
        grading.save(update_fields=["status", "current_marker_index", "updated_at"])
        return {
            "action": "in_progress",
            "status": grading.status,
            "detail": f"Konsensus yoxdur, növbəti marker gözlənilir ({graded_count}/{required_count})",
        }
    else:
        # Hamı qiymətləndirib, konsensus yoxdur → Baş Markerə
        grading.status = StudentAnswerGrading.Status.HEAD_MARKER
        grading.save(update_fields=["status", "updated_at"])
        return {
            "action": "escalated_to_head_marker",
            "status": grading.status,
            "detail": "Konsensus yoxdur, Baş Markerə göndərildi",
        }


def get_head_marker_queue(marker: Marker):
    """
    Baş Marker üçün gözləyən elementləri qaytarır.
    Müəllim `allowed_subjects`-dəki fənlər üzrə.
    Şübhəlilər əvvəl (spesifikasiya düzəlişi: -is_suspicious).
    """
    allowed_subject_names = marker.allowed_subjects.values_list(
        "subject_name", flat=True
    )

    return StudentAnswerGrading.objects.filter(
        status=StudentAnswerGrading.Status.HEAD_MARKER,
        subject_name__in=allowed_subject_names,
    ).select_related("result", "assignment").order_by(
        "-is_suspicious", "created_at"
    )


def create_answer_gradings_for_session(session: StudentExamSession):
    """
    Seans bitdikdən sonra açıq suallar üçün StudentAnswerGrading yarat.
    Lazım olan hər (exam, subject, question_number) üçün bir grading.
    """
    assignment = session.assignment
    exam_id = assignment.exam_id

    # Seansın cavablarını götür
    answers = session.answers.all()

    # Cavab açarlarından açıq sualları aşkarla
    from ..models.exam_core import CorrectAnswerKey

    correct_keys = CorrectAnswerKey.objects.filter(
        exam_id=exam_id,
        is_online=True,
    ).select_related("subject")

    for key in correct_keys:
        for q_data in key.answers_data:
            q_num = q_data.get("question_number")
            q_type = q_data.get("question_type", "")
            marker_check = q_data.get("marker_check", False)

            # Açıq tip və ya marker_check tələb edən sual
            if marker_check or _is_open_ended(q_type):
                # Şagird cavabını yoxla
                student_answer = answers.filter(question_number=q_num).first()
                if student_answer and not _is_trivial_answer(student_answer.answer):
                    # QuestionAssignment tap və ya yarat
                    qa, _ = QuestionAssignment.objects.get_or_create(
                        exam_id=exam_id,
                        subject=key.subject,
                        question_number=q_num,
                        defaults={"required_marker_count": 1},
                    )

                    # StudentAnswerGrading yarat (pending)
                    StudentAnswerGrading.objects.get_or_create(
                        result=session.result,
                        assignment=qa,
                        subject_name=key.subject.subject_name,
                        question_number=q_num,
                        defaults={"status": StudentAnswerGrading.Status.PENDING},
                    )
