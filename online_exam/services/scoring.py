"""
Bölmə 6: Qiymətləndirmə alqoritmi (avtomatik scoring)
Bölmə 7: Marker konsensus sistemi

Submit anında hər fənn üçün icra olunur.
"""
import re
import math
from decimal import Decimal, ROUND_HALF_UP
from typing import Any


FRACTION_MAP = {
    "0": Decimal("0"),
    "1/3": Decimal("0.333333"),
    "1/2": Decimal("0.5"),
    "2/3": Decimal("0.666667"),
    "1": Decimal("1"),
}


def _normalize_answer(answer: str) -> str:
    """Cavabı normallaşdır — boşluqları sil, böyük hərflə yaz."""
    if not answer:
        return ""
    return answer.strip().upper()


def _normalize_matching(answer: str) -> str:
    """
    Uyğunlaşdırma cavabını normallaşdır:
    Orijinal: "1-A,2-C,3-B" → sıralanmış: "1-A,2-C,3-B"
    Qayda: nömrələr üzrə artan sıra.
    """
    if not answer:
        return ""
    parts = [p.strip() for p in answer.split(",") if p.strip()]
    parsed = []
    for p in parts:
        match = re.match(r"(\d+)\s*[-–]\s*(\S+)", p)
        if match:
            parsed.append((int(match.group(1)), match.group(2).upper()))
    parsed.sort(key=lambda x: x[0])
    return ",".join(f"{num}-{ans}" for num, ans in parsed)


def _normalize_correct_matching(answer: str) -> str:
    """
    Cavab açarındakı uyğunlaşdırma cavabını normallaşdır:
    "C;BE;D" → "1-C,2-BE,3-D"
    """
    if not answer:
        return ""
    parts = [p.strip().upper() for p in answer.split(";") if p.strip()]
    result = []
    for i, part in enumerate(parts, 1):
        result.append(f"{i}-{part}")
    return ",".join(result)


def _is_open_ended(question_type: str) -> bool:
    """Sual açıq tiplidirmi? (marker tərəfindən qiymətləndirilməli)"""
    qt = question_type.lower()
    if "kodlaşd" in qt or "kodlaşır" in qt:
        return False
    return "açıq" in qt or "esse" in qt


def _is_trivial_answer(answer: str) -> bool:
    """Cavab trivialdırmı? (boş, 0, -, ., none, ...)"""
    if not answer:
        return True
    normalized = answer.strip().lower()
    return normalized in ("", "0", "-", ".", "none", "boş", "")


def _fraction_to_decimal(fraction_str: str) -> Decimal:
    """Fraksiya stringini Decimal-a çevir."""
    return FRACTION_MAP.get(fraction_str.strip(), Decimal("0"))


def _round_score(value: Decimal, places: int = 3) -> Decimal:
    """ROUND_HALF_UP ilə yuvarlaqlaşdır."""
    return value.quantize(Decimal(10) ** -places, rounding=ROUND_HALF_UP)


def calculate_subject_score(
    answers_data: list[dict],
    student_answers: dict[int, str],
    open_ended_scores: dict | None = None,
    is_online: bool = True,
) -> dict:
    """
    Bir fənn üçün qiymətləndirməni hesablayır.

    Args:
        answers_data: Cavab açarının answers_data JSON-u (sual siyahısı)
        student_answers: {question_number: answer_string} — şagird cavabları
        open_ended_scores: {question_number: fraction_string} — marker balları (fraksiya)
        is_online: Online imtahandırmı?

    Returns:
        {
            "point": Decimal,       — fənn üzrə cəmi bal
            "correct": int,
            "wrong": int,
            "empty": int,
            "open_ended_scores": dict,
            "details": [
                {
                    "question_number": int,
                    "question_type": str,
                    "is_open_ended": bool,
                    "student_ans": str,
                    "correct_ans": str,
                    "result": str,          — correct/wrong/empty/open_ended_pending/open_ended_scored/open_ended_empty
                    "earned_points": Decimal,
                    "raw_fraction": str,
                }
            ]
        }
    """
    if open_ended_scores is None:
        open_ended_scores = {}

    details = []
    total_point = Decimal("0")
    correct_count = 0
    wrong_count = 0
    empty_count = 0
    open_ended_updated = {}

    for q in answers_data:
        q_num = q["question_number"]
        q_type = q.get("question_type", "Qapalı")
        correct_answer = q.get("correct_answer", "")
        points = Decimal(str(q.get("points", 0)))
        penalty = Decimal(str(q.get("penalty_points", 0)))
        is_starred = q.get("is_starred", False)
        open_ended = _is_open_ended(q_type)

        student_ans = student_answers.get(q_num, "")
        student_ans_str = str(student_ans).strip()

        detail = {
            "question_number": q_num,
            "question_type": q_type,
            "is_open_ended": open_ended,
            "student_ans": student_ans_str,
            "correct_ans": str(correct_answer),
            "result": "empty",
            "earned_points": Decimal("0"),
            "raw_fraction": "",
        }

        if open_ended:
            # Açıq/esse sual — marker qiymətləndirməlidir
            if _is_trivial_answer(student_ans_str):
                # Trivial cavab → avtomatik 0
                detail["result"] = "open_ended_scored"
                detail["earned_points"] = Decimal("0")
                detail["raw_fraction"] = "0"
                open_ended_updated[q_num] = "0"
                empty_count += 1
            elif q_num in open_ended_scores:
                # Marker balı var
                frac_str = str(open_ended_scores[q_num])
                frac_dec = _fraction_to_decimal(frac_str)
                earned = _round_score(frac_dec * points)
                detail["result"] = "open_ended_scored"
                detail["earned_points"] = earned
                detail["raw_fraction"] = frac_str
                open_ended_updated[q_num] = frac_str
                total_point += earned
            else:
                # Marker balı yoxdur → pending
                detail["result"] = "open_ended_pending"
                empty_count += 1
        else:
            # Avtomatik qiymətləndirmə
            if _is_trivial_answer(student_ans_str):
                # Boş cavab
                if is_starred and not is_online:
                    # Offline ulduzlu: boş qalsa da tam bal
                    detail["result"] = "correct"
                    detail["earned_points"] = points
                    total_point += points
                    correct_count += 1
                else:
                    detail["result"] = "empty"
                    empty_count += 1
            else:
                # Cavab var — müqayisə et
                norm_student = _normalize_answer(student_ans_str)
                norm_correct = _normalize_answer(str(correct_answer))

                is_match = False

                if q_type == "Uyğunlaşdırma":
                    # Uyğunlaşdırma xüsusi müqayisə
                    norm_student_matching = _normalize_matching(student_ans_str)
                    norm_correct_full = _normalize_correct_matching(str(correct_answer))
                    norm_correct_matching = _normalize_matching(norm_correct_full)
                    is_match = norm_student_matching == norm_correct_matching
                elif q_type == "Kodlaşdırıla bilən açıq tipli":
                    # Rəqəm/simvol müqayisəsi (float bərabərlik)
                    try:
                        is_match = float(norm_student) == float(norm_correct)
                    except (ValueError, TypeError):
                        is_match = False
                else:
                    # Bağlı / Doğru-Yanlış — böyük hərf bərabərliyi
                    is_match = norm_student == norm_correct

                if is_match:
                    detail["result"] = "correct"
                    detail["earned_points"] = points
                    total_point += points
                    correct_count += 1
                else:
                    detail["result"] = "wrong"
                    if penalty > 0:
                        detail["earned_points"] = -penalty
                        total_point -= penalty
                    wrong_count += 1

        details.append(detail)

    return {
        "point": _round_score(total_point, 4),
        "correct": correct_count,
        "wrong": wrong_count,
        "empty": empty_count,
        "open_ended_scores": open_ended_updated,
        "details": details,
    }


def score_full_session(
    answer_keys: list,
    student_answers_data: dict[str, dict[int, str]],
    open_ended_scores: dict[str, dict[int, str]] | None = None,
    is_online: bool = True,
) -> dict:
    """
    Tam seans üçün bütün fənlər üzrə qiymətləndirmə.

    Args:
        answer_keys: Seçilmiş cavab açarları (CorrectAnswerKey queryset/list)
        student_answers_data: {"Riyaziyyat": {1: "A", 2: "B", ...}, "Azərbaycan dili": ...}
        open_ended_scores: {"Riyaziyyat": {5: "2/3"}, ...}
        is_online: Online imtahandırmı?

    Returns:
        {
            "total_point": Decimal,
            "is_manual_check_pending": bool,
            "status": "pending_manual" | "graded",
            "result_details": { subject_name: {...} },
            "result_compact": { subject_name: "ABCDA..." },
        }
    """
    if open_ended_scores is None:
        open_ended_scores = {}

    result_details = {}
    result_compact = {}
    total_point = Decimal("0")
    is_manual_check_pending = False

    for key in answer_keys:
        subject = key.subject.subject_name
        answers_data = key.answers_data or []
        student_ans = student_answers_data.get(subject, {})
        oe_scores = open_ended_scores.get(subject, {})

        subject_result = calculate_subject_score(
            answers_data=answers_data,
            student_answers=student_ans,
            open_ended_scores=oe_scores,
            is_online=is_online,
        )

        result_details[subject] = {
            "point": float(subject_result["point"]),
            "correct": subject_result["correct"],
            "wrong": subject_result["wrong"],
            "empty": subject_result["empty"],
            "open_ended_scores": subject_result["open_ended_scores"],
            "details": [
                {
                    **d,
                    "earned_points": float(d["earned_points"]),
                }
                for d in subject_result["details"]
            ],
        }

        # Compact cavab stringi
        compact = ""
        for d in subject_result["details"]:
            # Hər sual üçün qısa status
            if d["result"] == "correct":
                compact += "D"
            elif d["result"] == "wrong":
                compact += "Y"
            elif d["result"] == "empty":
                compact += "B"
            elif "open_ended" in d["result"]:
                compact += "?"
            else:
                compact += "B"
        result_compact[subject] = compact

        total_point += subject_result["point"]

        if any(d["result"] == "open_ended_pending" for d in subject_result["details"]):
            is_manual_check_pending = True

    return {
        "total_point": float(_round_score(total_point, 2)),
        "is_manual_check_pending": is_manual_check_pending,
        "status": "pending_manual" if is_manual_check_pending else "graded",
        "result_details": result_details,
        "result_compact": result_compact,
    }
