"""
Bölmə 3: Variant Seçim Alqoritmi

Şagird imtahana başlayanda hansı sual dəstini alır?
"""
from typing import Optional
from django.db.models import Q


def select_answer_keys(
    exam_id: int,
    variant_name: Optional[str],
    sinif_id: Optional[int] = None,
    bolme_id: Optional[int] = None,
    qrup_id: Optional[int] = None,
) -> list:
    """
    Verilən imtahan üçün cavab açarlarını seçir.

    Alqoritm (spesifikasiya Bölmə 3):
    1. Bütün CorrectAnswerKey-ləri götür, subject_order-a görə sırala.
    2. sinif_id, bolme_id, qrup_id-yə görə filtrlə (kombinasiya uyğunluğu).
    3. variant_name verilibsə ona filtrlə; yoxdursa mövcud variantlardan birincisini seç.
    4. Zərif geriyə çəkilmə (fallback):
       - Dəqiq variant + sinif → dəqiq
       - Sinif yoxdursa → null-sinif variantını götür
       - Bölmə → qrup səviyyəsində tolerant fallback

    Returns:
        CorrectAnswerKey queryset (sorted by subject_order)
    """
    from ..models.exam_core import CorrectAnswerKey

    base_qs = CorrectAnswerKey.objects.filter(exam_id=exam_id)

    if variant_name:
        # 1. Dəqiq variant ilə başla
        qs = base_qs.filter(variant_name=variant_name)
    else:
        qs = base_qs

    # 2. Kombinasiya filtrləməsi (tolerant fallback ilə)
    filtered = _apply_combination_filter(qs, sinif_id, bolme_id, qrup_id)

    # 3. Əgər nəticə yoxdursa, fallback ilə yenidən cəhd et
    if not filtered.exists():
        # Sinif olmadan
        filtered = _apply_combination_filter(qs, None, bolme_id, qrup_id)

    if not filtered.exists():
        # Bölmə və qrup olmadan
        filtered = _apply_combination_filter(qs, None, None, None)

    if not filtered.exists() and variant_name:
        # Variant olmadan
        filtered = _apply_combination_filter(base_qs, sinif_id, bolme_id, qrup_id)

    if not filtered.exists():
        # Ən pis halda: variant da, kombinasiya da olmadan
        filtered = base_qs

    return list(filtered.order_by("subject_order", "key_id"))


def _apply_combination_filter(qs, sinif_id, bolme_id, qrup_id):
    """
    Kombinasiya filtri — tolerant məntiq:
    - Verilmiş dəyər varsa → həmin dəyər və ya null (tolerant)
    - Verilmiş dəyər yoxdursa → hər hansı dəyər (həm dəqiq, həm null)
    """
    q = Q()

    if sinif_id is not None:
        q &= Q(Q(sinif_id=sinif_id) | Q(sinif_id__isnull=True))
    # sinif_id None → hər hansı sinif (filter yox)

    if bolme_id is not None:
        q &= Q(Q(bolme_id=bolme_id) | Q(bolme_id__isnull=True))

    if qrup_id is not None:
        q &= Q(Q(qrup_id=qrup_id) | Q(qrup_id__isnull=True))

    return qs.filter(q)


def get_variant_choices(exam_id: int) -> list[str]:
    """Müvcud variantların siyahısını qaytarır."""
    from ..models.exam_core import CorrectAnswerKey

    variants = (
        CorrectAnswerKey.objects.filter(exam_id=exam_id)
        .values_list("variant_name", flat=True)
        .distinct()
    )
    return list(variants)


def get_exam_online_state(exam_id: int) -> dict:
    """
    Online imtahanın cari vəziyyətini hesablayır.

    Returns:
        {
            "state": "upcoming" | "active" | "ended" | "completed",
            "start_datetime": datetime | None,
            "end_datetime": datetime | None,
            "duration_hours": float,
        }
    """
    from datetime import datetime, time
    from django.utils import timezone
    from ..models.exam_core import CorrectAnswerKey

    keys = CorrectAnswerKey.objects.filter(
        exam_id=exam_id, is_online=True
    ).first()

    if not keys:
        return {"state": "ended", "start_datetime": None, "end_datetime": None, "duration_hours": 0}

    now = timezone.now()

    start_dt = None
    end_dt = None

    if keys.online_start_date and keys.online_start_time:
        start_dt = timezone.make_aware(
            datetime.combine(keys.online_start_date, keys.online_start_time)
        )

    if keys.online_end_date and keys.online_end_time:
        end_dt = timezone.make_aware(
            datetime.combine(keys.online_end_date, keys.online_end_time)
        )

    if start_dt and now < start_dt:
        state = "upcoming"
    elif end_dt and now > end_dt:
        state = "ended"
    else:
        state = "active"

    return {
        "state": state,
        "start_datetime": start_dt,
        "end_datetime": end_dt,
        "duration_hours": keys.online_duration_hours,
    }
