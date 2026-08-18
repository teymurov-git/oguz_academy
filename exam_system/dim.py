from decimal import Decimal

DIM_EXAM_TYPE_BURAXILIS = 'buraxilis'
DIM_EXAM_TYPE_BLOK = 'blok'

DIM_EXAM_TYPE_CHOICES = [
    (DIM_EXAM_TYPE_BURAXILIS, 'Buraxılış'),
    (DIM_EXAM_TYPE_BLOK, 'Blok'),
]

DIM_GROUP_CHOICES = [
    ('1', 'I qrup'),
    ('2', 'II qrup'),
    ('3', 'III qrup'),
    ('4', 'IV qrup'),
]

DIM_SUBTYPE_CHOICES = [
    ('', 'Standart'),
    ('ri', 'Rİ — Riyaziyyat, Fizika, İnformatika'),
    ('rk', 'RK — Riyaziyyat, Fizika, Kimya'),
    ('tc', 'TC — Ana dili, Tarix, Coğrafiya'),
    ('dt', 'DT — Ana dili, Tarix, Ədəbiyyat'),
]

# ══════════════════════════════════════════════════════════════════════════════
# DİM/OTK bal hesablama konfiqurasiyası
# ──────────────────────────────────────────────────────────────────────────────
# Gələcəkdə fənnlərin sayı və ya çəki əmsalları dəyişərsə YALNIZ bu konfiqurasiya
# yenilənməlidir — hesablama məntiqi (compute_dim_result) dəyişmir.
#
# Məntiq:
#   • Hər fənn əvvəlcə OTK alqoritmi ilə 0–100 nisbi bal şəklində hesablanır.
#   • Sonra çəki əmsalı tətbiq edilir.
#   • Buraxılış balı = Σ(fənn balı × 1.0)              → maks 300
#   • Blok balı     = Σ(fənn balı × çəki əmsalı)       → maks 400
#   • Yekun bal     = Buraxılış balı + Blok balı       → maks 700
# ══════════════════════════════════════════════════════════════════════════════

# ── Buraxılış imtahanı (11-ci sinif) — sabit 3 fənn, cərimə yoxdur ──────────
BURAXILIS_SUBJECTS = [
    {'subject': 'Tədris dili', 'weight': Decimal('1.0')},
    {'subject': 'Riyaziyyat', 'weight': Decimal('1.0')},
    {'subject': 'Xarici dil', 'weight': Decimal('1.0')},
]

# Buraxılış imtahanının sual strukturu — fənn üzrə bloklar və hər blokun balı.
#   'qapali'        → A–E seçimli, düzgün cavab admin paneldə hərflə daxil edilir.
#   'kodlasdirilan' → cavabı yalnız kodlaşdırılan açıq sual, admin text daxil edir.
#   'aciq'          → tam açıq sual, cavab admin paneldə yoxdur; yalnız yoxlamada
#                     1, 1/3, 2/3, 1/2 əmsalları ilə qiymətləndirilir.
BURAXILIS_STRUCTURE = [
    {
        'subject': 'Tədris dili',
        'weight': Decimal('1.0'),
        'blocks': [
            {'type': 'qapali', 'count': 18, 'points': Decimal('2.5')},
            {'type': 'aciq', 'count': 2, 'points': Decimal('5.0')},
            {'type': 'qapali', 'count': 8, 'points': Decimal('2.5')},
            {'type': 'aciq', 'count': 2, 'points': Decimal('5.0')},
        ],
    },
    {
        'subject': 'Riyaziyyat',
        'weight': Decimal('1.0'),
        'blocks': [
            {'type': 'qapali', 'count': 13, 'points': Decimal('3.1')},
            {'type': 'kodlasdirilan', 'count': 8, 'points': Decimal('3.1')},
            {'type': 'aciq', 'count': 4, 'points': Decimal('6.3')},
        ],
    },
    {
        'subject': 'Xarici dil',
        'weight': Decimal('1.0'),
        'blocks': [
            {'type': 'qapali', 'count': 5, 'points': Decimal('2.7')},
            {'type': 'aciq', 'count': 1, 'points': Decimal('5.4')},
            {'type': 'qapali', 'count': 16, 'points': Decimal('2.7')},
            {'type': 'qapali', 'count': 5, 'points': Decimal('2.7')},
            {'type': 'aciq', 'count': 3, 'points': Decimal('5.4')},
        ],
    },
]

# Açıq sualların qiymətləndirmə əmsalları (1, 1/3, 2/3, 1/2, 0)
OPEN_FRACTIONS = ['1', '1/3', '2/3', '1/2', '0']

# ── Blok (qəbul) imtahanı — I-IV ixtisas qrupları ───────────────────────────
# Hər qrupun fənn dəsti və çəki əmsalları DİM-ə uyğun.
GROUPS = {
    '1': {
        'ri': [
            {'subject': 'Riyaziyyat', 'weight': Decimal('1.5')},
            {'subject': 'Fizika', 'weight': Decimal('1.5')},
            {'subject': 'İnformatika', 'weight': Decimal('1.0')},
        ],
        'rk': [
            {'subject': 'Riyaziyyat', 'weight': Decimal('1.5')},
            {'subject': 'Fizika', 'weight': Decimal('1.5')},
            {'subject': 'Kimya', 'weight': Decimal('1.0')},
        ],
    },
    '2': {
        '': [
            {'subject': 'Riyaziyyat', 'weight': Decimal('1.5')},
            {'subject': 'Coğrafiya', 'weight': Decimal('1.5')},
            {'subject': 'Tarix', 'weight': Decimal('1.0')},
        ],
    },
    '3': {
        'tc': [
            {'subject': 'Ana dili', 'weight': Decimal('1.5')},
            {'subject': 'Tarix', 'weight': Decimal('1.5')},
            {'subject': 'Coğrafiya', 'weight': Decimal('1.0')},
        ],
        'dt': [
            {'subject': 'Ana dili', 'weight': Decimal('1.5')},
            {'subject': 'Tarix', 'weight': Decimal('1.5')},
            {'subject': 'Ədəbiyyat', 'weight': Decimal('1.0')},
        ],
    },
    '4': {
        '': [
            {'subject': 'Biologiya', 'weight': Decimal('1.5')},
            {'subject': 'Kimya', 'weight': Decimal('1.5')},
            {'subject': 'Fizika', 'weight': Decimal('1.0')},
        ],
    },
}

# Köhnə istinadlar üçün alias
SUBJECT_PLANS = GROUPS

QUESTIONS_PER_SUBJECT = 30
ANSWER_OPTIONS = ['A', 'B', 'C', 'D', 'E']

# Blok (qəbul) imtahanı fənn sual strukturu — hər fənn 30 sual:
#   22 qapalı (A–E seçimli, düzgün cavab admin paneldə hərflə) +
#   5 kodlaşdırılan açıq (cavab admin paneldə mətnlə) +
#   3 tam açıq (cavab admin paneldə YOX — yalnız nəticə yoxlanarkən qiymətləndirilir).
# Tam açıq sualların cavabı "Düzgün Cavablar" səhifəsində daxil edilmir;
# onlar buraxılış imtahanındakı 'aciq' suallar kimi markerlə qiymətləndirilir.
BLOK_STRUCTURE = [
    {'type': 'qapali', 'count': 22, 'points': Decimal('1')},
    {'type': 'kodlasdirilan', 'count': 5, 'points': Decimal('1')},
    {'type': 'aciq', 'count': 3, 'points': Decimal('1')},
]

# Blok (qəbul) fənni üçün OTK/DİM cəriməsi: NB = (Dq − ¼·Yq) × 100 / N
PENALTY_FACTOR = Decimal('0.25')

# Maksimum ballar
MAX_BURAXILIS = Decimal('300')
MAX_BLOK = Decimal('400')
MAX_YEKUN = Decimal('700')


def get_subjects(exam):
    """İmtahanın fənn konfiqurasiyasını (list of {subject, weight}) qaytarır."""
    if getattr(exam, 'dim_type', None) == DIM_EXAM_TYPE_BURAXILIS:
        return BURAXILIS_SUBJECTS
    plan = GROUPS.get(str(getattr(exam, 'exam_group', '')) or '', {})
    subtype = getattr(exam, 'group_subtype', '') or ''
    if subtype not in plan:
        subtype = list(plan.keys())[0] if plan else ''
    return plan.get(subtype, [])


def get_subject_names(exam):
    return [item['subject'] for item in get_subjects(exam)]


def get_buraxilis_structure():
    """Buraxılış imtahanının fənn üzrə sual strukturunu qaytarır."""
    return BURAXILIS_STRUCTURE


def get_blok_structure():
    """Blok (qəbul) imtahanı fənninin sual strukturunu qaytarır (22+5+3)."""
    return BLOK_STRUCTURE


def get_buraxilis_subject_count(subject_name):
    """Verilmiş fənn üçün ümumi sual sayını qaytarır."""
    for item in BURAXILIS_STRUCTURE:
        if item['subject'] == subject_name:
            return sum(b['count'] for b in item['blocks'])
    return 0


def get_question_grading(question):
    """Sualın qiymətləndirmə metodunu qaytarır: 'auto' | 'fixed' | 'coefficient'."""
    return (question.answers_data or {}).get('grading') or 'auto'


def compute_buraxilis_result(student_exam):
    """Buraxılış imtahanı — birbaşa sual balları ilə hesablanır.

    Qayda:
      • 'qapali'   → seçilən hərf düzgündürsə q.points, əks halda 0.
      • 'fixed'    → markerin daxil etdiyi points_earned (0..q.points).
      • 'coefficient' → markerin əmsalı (1, 1/3, 2/3, 1/2) ilə: bal = əmsal × q.points.
    """
    exam = student_exam.exam
    answers = {sa.question_id: sa for sa in student_exam.answers.all()}
    questions = list(exam.questions.filter(is_active=True).order_by('sort_order', 'created_at'))

    total_bal = Decimal('0')
    total_dq = 0
    total_yq = 0
    total_empty = 0
    per_subject = []

    for item in get_subjects(exam):
        subject_name = item['subject']
        weight = item['weight']
        subj_qs = [q for q in questions if q.subject == subject_name]

        dq = yq = empty = 0
        subject_bal = Decimal('0')

        for q in subj_qs:
            sa = answers.get(q.pk)
            grading = get_question_grading(q)
            if grading == 'coefficient':
                if sa is None or not (sa.text_answer or sa.points_earned):
                    empty += 1
                    continue
                earned = sa.points_earned or Decimal('0')
                subject_bal += earned
                if earned > 0:
                    dq += 1
                else:
                    yq += 1
            elif q.question_type in ('single_choice', 'multiple_choice', 'true_false'):
                if sa is None or not (sa.selected_option_ids or []):
                    empty += 1
                    continue
                sel = str(sa.selected_option_ids[0]).strip().upper()
                correct = (q.answers_data or {}).get('correct')
                if correct and sel == correct:
                    dq += 1
                    subject_bal += q.points
                else:
                    yq += 1
            else:
                # 'fixed' (kodlaşdırılan açıq) və ya digər mətn sualları
                if sa is None or not sa.text_answer.strip():
                    empty += 1
                    continue
                earned = sa.points_earned or Decimal('0')
                subject_bal += earned
                if earned > 0:
                    dq += 1
                else:
                    yq += 1

        total_dq += dq
        total_yq += yq
        total_empty += empty
        total_bal += subject_bal

        per_subject.append({
            'name': subject_name,
            'weight': weight,
            'coeff': weight,
            'dq': dq,
            'yq': yq,
            'empty': empty,
            'nb': subject_bal,
            'bal': subject_bal,
            'questions': subj_qs,
        })

    max_bal = sum((q.points for q in questions), Decimal('0'))
    total_bal = total_bal.quantize(Decimal('0.1'))
    max_bal = max_bal.quantize(Decimal('0.1'))

    return {
        'per_subject': per_subject,
        'total_bal': total_bal,
        'max_bal': max_bal,
        'dq': total_dq,
        'yq': total_yq,
        'empty': total_empty,
    }


def get_correct_letter(question):
    """Sualın düzgün cavab hərfini qaytarır (A–E) və ya None."""
    return (question.answers_data or {}).get('correct')


def is_dim_exam(exam):
    return bool(getattr(exam, 'dim_type', None))


def _subject_nb(dim_type, dq, yq, n):
    """Fənn üzrə 0–100 nisbi bal (OTK alqoritmi). n = sual sayı."""
    if dim_type == DIM_EXAM_TYPE_BURAXILIS:
        # Buraxılış: cərimə yoxdur — NB = Dq × 100 / N
        raw = Decimal(dq)
    else:
        # Blok (qəbul): NB = (Dq − ¼·Yq) × 100 / N, mənfi olarsa 0
        raw = Decimal(dq) - PENALTY_FACTOR * Decimal(yq)
    return (max(raw, Decimal('0')) * 100 / Decimal(n)).quantize(Decimal('0.1'))


def compute_dim_result(exam, student_answers, student_exam=None):
    """DİM balını hesablayır.

    student_answers: dict {question_id_str: seçilmiş hərf ('A'..'E') və ya ''}
    student_exam: StudentExam obyekti (Buraxılış imtahanı üçün tələb olunur —
                  açıq sualların marker balları buradan oxunur).
    Qaytarma: {'per_subject': [...], 'total_bal': Decimal, 'max_bal': Decimal,
               'dq','yq','empty'}
    """
    if (exam.dim_type or '') == DIM_EXAM_TYPE_BURAXILIS:
        if student_exam is not None:
            return compute_buraxilis_result(student_exam)
        # student_exam yoxdursa: açıq suallar 0 sayılır, qapalı suallar hesablanır.
        student_exam_lite = type('SE', (), {'exam': exam, 'answers': []})()
        return compute_buraxilis_result(student_exam_lite)

    subjects = get_subjects(exam)
    dim_type = exam.dim_type or DIM_EXAM_TYPE_BLOK
    total_bal = Decimal('0.00')
    total_dq = 0
    total_yq = 0
    total_empty = 0

    answers_map = {}
    if student_exam is not None:
        answers_map = {sa.question_id: sa for sa in student_exam.answers.all()}

    per_subject = []
    for item in subjects:
        subject_name = item['subject']
        weight = item['weight']
        questions = list(
            exam.questions.filter(subject=subject_name, is_active=True)
            .order_by('sort_order', 'created_at')
        )
        n = len(questions) or 1

        dq = yq = empty = 0
        dkod = Decimal('0')
        dyazili = Decimal('0')
        for q in questions:
            if q.question_type in ('text', 'matching', 'ordering'):
                # Açıq sual — markerin daxil etdiyi bal.
                # Kodlaşdırılan (grading='fixed') 1 dəfə, tam açıq yazılı (grading='coefficient') 2× sayılır.
                sa = answers_map.get(q.pk)
                if sa is None or not (sa.text_answer.strip() or (sa.points_earned or Decimal('0'))):
                    empty += 1
                    continue
                earned = sa.points_earned or Decimal('0')
                if get_question_grading(q) == 'coefficient':
                    dyazili += earned
                else:
                    dkod += earned
                continue
            choice = (student_answers.get(str(q.id)) or '').strip().upper()
            if not choice:
                empty += 1
                continue
            correct = get_correct_letter(q)
            if correct and choice == correct:
                dq += 1
            else:
                yq += 1

        # DİM blok düsturu (II mərhələ):
        #   NBq = (Dq − ¼·Yq) × 100/33  (mənfi olarsa 0)
        #   NBa = (Dkod + 2·Dyazılı) × 100/33
        #   NB  = NBq + NBa   (maks hər fənn 100)
        nbq = (max(Decimal(dq) - PENALTY_FACTOR * Decimal(yq), Decimal('0'))
               * 100 / Decimal('33')).quantize(Decimal('0.1'))
        nba = ((dkod + Decimal('2') * dyazili) * 100 / Decimal('33')).quantize(Decimal('0.1'))
        nb = (nbq + nba).quantize(Decimal('0.1'))
        subject_bal = (nb * weight).quantize(Decimal('0.1'))
        total_bal += subject_bal
        total_dq += dq
        total_yq += yq
        total_empty += empty

        per_subject.append({
            'name': subject_name,
            'weight': weight,
            'coeff': weight,          # geri uyğunluq üçün alias
            'dq': dq,
            'yq': yq,
            'empty': empty,
            'nb': nb,
            'bal': subject_bal,
            'questions': questions,
        })

    max_bal = MAX_BURAXILIS if dim_type == DIM_EXAM_TYPE_BURAXILIS else MAX_BLOK
    total_bal = total_bal.quantize(Decimal('0.1'))

    return {
        'per_subject': per_subject,
        'total_bal': total_bal,
        'max_bal': max_bal,
        'dq': total_dq,
        'yq': total_yq,
        'empty': total_empty,
    }


def compute_yekun_bal(buraxilis_bal, blok_bal):
    """Yekun bal = Buraxılış balı + Blok balı (maks 700)."""
    buraxilis = Decimal(buraxilis_bal or 0)
    blok = Decimal(blok_bal or 0)
    return {
        'buraxilis_bal': buraxilis,
        'blok_bal': blok,
        'yekun_bal': (buraxilis + blok).quantize(Decimal('0.1')),
        'max_bal': MAX_YEKUN,
    }
