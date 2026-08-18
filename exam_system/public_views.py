from django.shortcuts import render
from django.db.models import Sum, Q
from decimal import Decimal

from exam_system.models import Exam, StudentExam, StudentAnswer
from exam_system.dim import compute_dim_result, compute_yekun_bal, is_dim_exam
from students.models import Student


def _calc_nb(student_exam, total_questions):
    all_answers = student_exam.answers.filter(question__is_active=True)
    mc_qs = all_answers.filter(question__question_type__in=['single_choice', 'multiple_choice', 'true_false'])
    dq = mc_qs.filter(is_correct=True).count()
    yq = mc_qs.filter(is_correct=False).count()
    open_answers = all_answers.filter(question__question_type__in=['text', 'matching', 'ordering'])
    da = float(open_answers.aggregate(Sum('points_earned'))['points_earned__sum'] or 0)
    nb = (Decimal(str(dq)) - Decimal('0.25') * Decimal(str(yq)) + Decimal(str(da))) * 100 / Decimal(str(33))
    return {
        'dq': dq,
        'yq': yq,
        'da': da,
        'empty': total_questions - all_answers.count(),
        'nb_score': round(min(float(nb), 100), 2),
        'total_score': float(all_answers.aggregate(Sum('points_earned'))['points_earned__sum'] or 0),
        'is_dim': False,
    }


def _get_answers_map(student_exam):
    ans = {}
    for sa in student_exam.answers.filter(question__is_active=True):
        letter = ''
        sel = sa.selected_option_ids or []
        if sel:
            letter = str(sel[0]).strip().upper()
        ans[str(sa.question_id)] = letter
    return ans


def _calc(student_exam, total_questions):
    if is_dim_exam(student_exam.exam):
        result = compute_dim_result(student_exam.exam, _get_answers_map(student_exam), student_exam=student_exam)
        return {
            'dq': result['dq'],
            'yq': result['yq'],
            'da': 0,
            'empty': result['empty'],
            'nb_score': float(result['total_bal']),
            'total_score': float(result['total_bal']),
            'is_dim': True,
            'dim_result': result,
        }
    return _calc_nb(student_exam, total_questions)


def _build_answer_cards(student_exam, calc, total_questions):
    """Cavab kartı — hər sual üçün tələbənin cavabı, düzgün cavab və status.

    DİM imtahanları üçün fənn bölmələrinə (subject_blocks) qruplaşdırılır.
    """
    exam = student_exam.exam
    questions = list(exam.questions.filter(is_active=True).order_by('sort_order', 'created_at'))

    answers_map = {}
    for sa in student_exam.answers.all():
        answers_map[sa.question_id] = sa

    cards = []
    for idx, q in enumerate(questions):
        ea = answers_map.get(q.pk)
        options = q.answers_data.get('options', [])
        correct_letter = (q.answers_data or {}).get('correct')
        if correct_letter:
            correct_ids = [correct_letter]
        else:
            correct_ids = [o['id'] for o in options if o.get('is_correct')]

        selected = []
        is_correct = None
        if ea:
            selected = ea.selected_option_ids or []
            is_correct = ea.is_correct

        if ea and (selected or ea.text_answer):
            status = 'correct' if is_correct else 'wrong'
        else:
            status = 'empty'

        student_letter = ''
        if selected:
            student_letter = str(selected[0]).strip().upper()
        correct_letter_str = ''
        if correct_ids:
            correct_letter_str = str(correct_ids[0]).strip().upper()

        cards.append({
            'question': q,
            'number': q.question_number or q.sort_order or idx + 1,
            'subject': q.subject or '—',
            'status': status,
            'student_letter': student_letter,
            'correct_letter': correct_letter_str,
            'text_answer': ea.text_answer if ea else '',
            'points_earned': ea.points_earned if ea else Decimal('0'),
            'answer': ea,
        })

    subject_blocks = []
    if calc.get('is_dim') and calc.get('dim_result'):
        by_subject = {}
        for c in cards:
            by_subject.setdefault(c['subject'], []).append(c)
        for s in calc['dim_result']['per_subject']:
            subject_blocks.append({
                'name': s['name'],
                'dq': s['dq'],
                'yq': s['yq'],
                'nb': s['nb'],
                'bal': s['bal'],
                'cards': by_subject.get(s['name'], []),
            })
    return {
        'is_dim': bool(calc.get('is_dim')),
        'subject_blocks': subject_blocks,
        'cards': cards,
    }


def public_results(request):
    """Tələbə iş nömrəsini yazır → bütün imtahan nəticələrini görür."""
    student_id_query = request.GET.get('sid', '').strip()
    student = None
    results = []
    search_error = ''

    if student_id_query:
        student = Student.objects.filter(
            Q(work_number__iexact=student_id_query) | Q(student_id__iexact=student_id_query)
        ).select_related('user').first()
        if student:
            student_exams = StudentExam.objects.filter(
                student=student
            ).select_related('exam').prefetch_related('answers__question').order_by('-exam__start_datetime')

            for se in student_exams:
                total_q = se.exam.total_questions or se.exam.questions.filter(is_active=True).count()
                calc = _calc(se, total_q)
                cards = _build_answer_cards(se, calc, total_q)
                results.append({
                    'student_exam': se,
                    'exam': se.exam,
                    **calc,
                    'cards': cards['cards'],
                    'subject_blocks': cards['subject_blocks'],
                    'cards_is_dim': cards['is_dim'],
                })
        else:
            search_error = f'"{student_id_query}" iş nömrəli şagird tapılmadı.'

    yekun = None
    if student:
        buraxilis = next((r for r in results if r['exam'].dim_type == 'buraxilis'), None)
        blok = next((r for r in results if r['exam'].dim_type == 'blok'), None)
        if buraxilis and blok:
            yekun = compute_yekun_bal(buraxilis['nb_score'], blok['nb_score'])

    context = {
        'student_id_query': student_id_query,
        'student': student,
        'results': results,
        'search_error': search_error,
        'yekun': yekun,
    }
    return render(request, 'exam_system/results.html', context)
