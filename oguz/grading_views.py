from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.db.models import Sum, Q
from django.contrib import messages
from django.urls import reverse
from decimal import Decimal, ROUND_HALF_UP
from django.utils.text import slugify
import uuid

from exam_system.models import Exam, Question, StudentExam, StudentAnswer
from exam_system.dim import compute_dim_result, compute_yekun_bal, is_dim_exam
from students.models import Student

OPEN_FRACTION_VALUES = {
    '0': Decimal('0'),
    '1': Decimal('1'),
    '1/3': Decimal('0.333333'),
    '2/3': Decimal('0.666667'),
    '1/2': Decimal('0.5'),
}


def _is_teacher(user):
    if hasattr(user, 'teacher_profile'):
        return True
    from roles.models import UserRole
    return UserRole.objects.filter(user=user, role__slug='muellim').exists()


def _get_answers_map(student_exam):
    """question_id -> seçilmiş hərf ('A'..'E') və ya ''"""
    ans = {}
    for sa in student_exam.answers.filter(question__is_active=True):
        letter = ''
        sel = sa.selected_option_ids or []
        if sel:
            letter = str(sel[0]).strip().upper()
        ans[str(sa.question_id)] = letter
    return ans


def _calc_nb(student_exam, total_questions):
    all_answers = student_exam.answers.filter(question__is_active=True)
    mc_qs = all_answers.filter(question__question_type__in=['single_choice', 'multiple_choice', 'true_false'])
    dq = mc_qs.filter(is_correct=True).count()
    yq = mc_qs.filter(is_correct=False).count()
    open_answers = all_answers.filter(question__question_type__in=['text', 'matching', 'ordering'])
    da = float(open_answers.aggregate(Sum('points_earned'))['points_earned__sum'] or 0)
    nb = (Decimal(str(dq)) - Decimal('0.25') * Decimal(str(yq)) + Decimal(str(da))) * 100 / Decimal(str(33))
    return {
        'dq': dq, 'yq': yq, 'da': da,
        'nb_score': round(min(float(nb), 100), 2),
        'total': float(all_answers.aggregate(Sum('points_earned'))['points_earned__sum'] or 0),
        'empty': total_questions - all_answers.count(),
        'is_dim': False,
    }


def _dim_calc(student_exam):
    """DİM sistemi üzrə bal hesabla (Buraxılış/Blok)."""
    result = compute_dim_result(student_exam.exam, _get_answers_map(student_exam), student_exam=student_exam)
    return {
        'dq': result['dq'],
        'yq': result['yq'],
        'da': 0,
        'nb_score': float(result['total_bal']),
        'total': float(result['total_bal']),
        'empty': result['empty'],
        'is_dim': True,
        'dim_result': result,
    }


def _calc(student_exam, total_questions):
    if is_dim_exam(student_exam.exam):
        return _dim_calc(student_exam)
    return _calc_nb(student_exam, total_questions)


def _save_dim_result(student_exam):
    """DİM nəticəsini StudentExam üzərində saxla."""
    res = compute_dim_result(student_exam.exam, _get_answers_map(student_exam), student_exam=student_exam)
    student_exam.dim_result = {
        'per_subject': [
            {
                'name': s['name'],
                'coeff': str(s['coeff']),
                'dq': s['dq'],
                'yq': s['yq'],
                'empty': s['empty'],
                'nb': str(s['nb']),
                'bal': str(s['bal']),
            }
            for s in res['per_subject']
        ],
        'total_bal': str(res['total_bal']),
        'max_bal': str(res['max_bal']),
    }
    student_exam.dim_total_bal = res['total_bal']
    student_exam.dim_max_bal = res['max_bal']
    student_exam.save(update_fields=['dim_result', 'dim_total_bal', 'dim_max_bal', 'updated_at'])
    return res


def _buraxilis_bal_map(student_ids):
    """student_id -> tələbənin ən son Buraxılış imtahan balı (Blok nəticəsində Yekun üçün)."""
    result = {}
    se_qs = (
        StudentExam.objects.filter(student_id__in=student_ids, exam__dim_type='buraxilis')
        .select_related('exam')
        .order_by('-exam__start_datetime')
    )
    for se in se_qs:
        if se.student_id not in result:
            result[se.student_id] = _dim_calc(se)['nb_score']
    return result


@staff_member_required
def grading_exam_list(request):
    """İmtahan siyahısı — iş nömrəsi ilə axtarış + yaratma."""
    user = request.user

    if request.method == 'POST':
        action = request.POST.get('action', '')

        if action == 'create_exam':
            title = request.POST.get('exam_title', '').strip()
            subject = request.POST.get('exam_subject', '').strip()
            q_count = request.POST.get('exam_total_questions', '0').strip()
            if title:
                slug = slugify(title) + '-' + uuid.uuid4().hex[:6]
                Exam.objects.create(
                    title=title,
                    slug=slug,
                    subject=subject,
                    total_questions=int(q_count) if q_count else 0,
                    exam_type='course',
                    status='draft',
                    is_active=True,
                    created_by=request.user,
                )
            return redirect('grading_exam_list')

        elif action == 'register_student':
            exam_id = request.POST.get('reg_exam_id')
            student_id_val = request.POST.get('reg_student_id', '').strip()
            if exam_id and student_id_val:
                exam = Exam.objects.filter(pk=exam_id).first()
                student = Student.objects.filter(
                    Q(work_number__iexact=student_id_val) | Q(student_id__iexact=student_id_val)
                ).first()
                if exam and student:
                    se, created = StudentExam.objects.get_or_create(
                        exam=exam, student=student,
                        defaults={'status': 'registered'}
                    )
                    if not created:
                        messages.info(request, f'{student.user.get_full_name()} artıq qeydiyyatdadır.')
                    else:
                        messages.success(request, f'{student.user.get_full_name()} ({student.student_id}) qeydiyyatdan keçdi.')
                else:
                    messages.error(request, 'İmtahan və ya tələbə tapılmadı.')
            return redirect(f"{reverse('grading_exam_list')}?exam_id={exam_id}")

    if _is_teacher(user):
        teacher = getattr(user, 'teacher_profile', None)
        if teacher:
            exams = Exam.objects.filter(
                Q(course__teacher=teacher) | Q(group__teacher=teacher),
                is_active=True
            ).distinct().select_related('course', 'group')
        else:
            exams = Exam.objects.none()
    else:
        exams = Exam.objects.filter(is_active=True).select_related('course', 'group')

    exam_id = request.GET.get('exam_id')
    student_id_query = request.GET.get('sid', '').strip()

    selected_exam = None
    student_exams = []
    found_student = None
    search_error = ''

    if exam_id:
        selected_exam = get_object_or_404(Exam, pk=exam_id)
        total_q = selected_exam.total_questions or selected_exam.questions.filter(is_active=True).count()

        if student_id_query:
            found_student = Student.objects.filter(
                Q(work_number__icontains=student_id_query) | Q(student_id__icontains=student_id_query)
            ).select_related('user').first()
            if found_student:
                se = StudentExam.objects.filter(
                    exam=selected_exam, student=found_student
                ).select_related('student__user').prefetch_related('answers__question').first()
                if se:
                    calc = _calc(se, total_q)
                    se.calc = calc
                    student_exams = [se]
                else:
                    search_error = f'"{student_id_query}" bu imtahana qeydiyyatdan keçməyib.'
            else:
                search_error = f'"{student_id_query}" nömrəli tələbə tapılmadı.'
        else:
            all_se = StudentExam.objects.filter(exam=selected_exam).select_related(
                'student__user'
            ).prefetch_related('answers__question')
            for se in all_se:
                se.calc = _calc(se, total_q)
            student_exams = list(all_se)

    context = {
        'title': 'Qiymətləndirmə',
        'exams': exams,
        'selected_exam': selected_exam,
        'student_exams': student_exams,
        'student_id_query': student_id_query,
        'found_student': found_student,
        'search_error': search_error,
    }
    return render(request, 'admin/grading/exam_list.html', context)


@staff_member_required
def grading_enter(request, exam_id, student_exam_id):
    """Tələbənin cavablarını daxil et / redaktə et."""
    exam = get_object_or_404(Exam, pk=exam_id)
    student_exam = get_object_or_404(StudentExam, pk=student_exam_id, exam=exam)

    questions = exam.questions.filter(is_active=True).order_by('sort_order', 'created_at')

    if request.method == 'POST':
        for q in questions:
            qtype = q.question_type
            if qtype in ('single_choice', 'true_false'):
                selected = request.POST.get(f'q_{q.pk}', '').strip()
                answer_obj, _ = StudentAnswer.objects.get_or_create(
                    student_exam=student_exam, question=q
                )
                answer_obj.selected_option_ids = [selected] if selected else []
                options = q.answers_data.get('options', [])
                correct_letter = (q.answers_data or {}).get('correct')
                if correct_letter:
                    answer_obj.is_correct = selected == correct_letter if selected else None
                else:
                    correct_ids = [o['id'] for o in options if o.get('is_correct')]
                    answer_obj.is_correct = selected in correct_ids if selected else None
                if answer_obj.is_correct:
                    answer_obj.points_earned = q.points
                else:
                    answer_obj.points_earned = Decimal('0')
                answer_obj.save()

            elif qtype == 'multiple_choice':
                selected = request.POST.getlist(f'q_{q.pk}')
                answer_obj, _ = StudentAnswer.objects.get_or_create(
                    student_exam=student_exam, question=q
                )
                answer_obj.selected_option_ids = selected
                options = q.answers_data.get('options', [])
                correct_ids = set(o['id'] for o in options if o.get('is_correct'))
                if correct_ids and set(selected) == correct_ids:
                    answer_obj.is_correct = True
                    answer_obj.points_earned = q.points
                elif not selected:
                    answer_obj.is_correct = None
                    answer_obj.points_earned = Decimal('0')
                else:
                    answer_obj.is_correct = False
                    answer_obj.points_earned = Decimal('0')
                answer_obj.save()

            elif qtype in ('text', 'matching', 'ordering'):
                text_val = request.POST.get(f'q_{q.pk}', '').strip()
                answer_obj, _ = StudentAnswer.objects.get_or_create(
                    student_exam=student_exam, question=q
                )
                answer_obj.text_answer = text_val
                grading = (q.answers_data or {}).get('grading') or 'auto'
                if grading == 'coefficient':
                    frac = request.POST.get(f'q_{q.pk}_frac', '').strip()
                    coeff = OPEN_FRACTION_VALUES.get(frac, Decimal('0'))
                    answer_obj.points_earned = (coeff * q.points).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                    answer_obj.selected_option_ids = [frac] if frac else []
                else:
                    score_val = request.POST.get(f'q_{q.pk}_score', '0').strip()
                    try:
                        answer_obj.points_earned = Decimal(score_val)
                    except Exception:
                        answer_obj.points_earned = Decimal('0')
                    answer_obj.selected_option_ids = []
                answer_obj.is_correct = answer_obj.points_earned > 0
                answer_obj.save()

        if is_dim_exam(exam):
            _save_dim_result(student_exam)

        return redirect('grading_enter', exam_id=exam.pk, student_exam_id=student_exam.pk)

    existing_answers = {}
    for sa in student_exam.answers.all():
        existing_answers[sa.question_id] = sa

    question_data = []
    for q in questions:
        ea = existing_answers.get(q.pk)
        options = q.answers_data.get('options', [])

        selected = []
        is_correct = None
        points_earned = Decimal('0')
        text_answer = ''

        if ea:
            selected = ea.selected_option_ids or []
            is_correct = ea.is_correct
            points_earned = ea.points_earned
            text_answer = ea.text_answer or ''

        correct_ids = [o['id'] for o in options if o.get('is_correct')]
        correct_letter = (q.answers_data or {}).get('correct')
        if correct_letter and correct_letter not in correct_ids:
            correct_ids.append(correct_letter)

        grading = (q.answers_data or {}).get('grading') or 'auto'
        frac_options = []
        if grading == 'coefficient':
            frac_options = [
                {'frac': f, 'points': (OPEN_FRACTION_VALUES[f] * q.points).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)}
                for f in OPEN_FRACTION_VALUES
            ]

        question_data.append({
            'question': q,
            'options': options,
            'selected': selected,
            'correct_ids': correct_ids,
            'is_correct': is_correct,
            'points_earned': points_earned,
            'text_answer': text_answer,
            'grading': grading,
            'frac_options': frac_options,
        })

    all_answers = student_exam.answers.all()
    total_score = float(all_answers.aggregate(Sum('points_earned'))['points_earned__sum'] or 0)
    max_score = float(questions.aggregate(Sum('points'))['points__sum'] or 0)

    mc_qs = all_answers.filter(question__question_type__in=['single_choice', 'multiple_choice', 'true_false'])
    mc_correct = mc_qs.filter(is_correct=True).count()
    mc_wrong = mc_qs.filter(is_correct=False).count()

    open_qs = all_answers.filter(question__question_type__in=['text', 'matching', 'ordering'])
    open_score = float(open_qs.aggregate(Sum('points_earned'))['points_earned__sum'] or 0)

    calc = _calc(student_exam, questions.count())
    dim_subjects = []
    if calc['is_dim']:
        for s in calc['dim_result']['per_subject']:
            dim_subjects.append({
                'name': s['name'],
                'coeff': s['coeff'],
                'dq': s['dq'],
                'yq': s['yq'],
                'empty': s['empty'],
                'nb': s['nb'],
                'bal': s['bal'],
            })

    context = {
        'title': f'{exam.title} — {student_exam.student}',
        'exam': exam,
        'student_exam': student_exam,
        'question_data': question_data,
        'total_score': total_score,
        'max_score': max_score,
        'mc_correct': mc_correct,
        'mc_wrong': mc_wrong,
        'open_score': open_score,
        'total_questions': questions.count(),
        'nb_score': calc['nb_score'],
        'dq': calc['dq'],
        'yq': calc['yq'],
        'da': calc['da'],
        'is_dim': calc['is_dim'],
        'dim_subjects': dim_subjects,
        'dim_total_bal': calc['nb_score'],
        'dim_max_bal': float(calc['dim_result']['max_bal']) if calc['is_dim'] else 0,
    }
    return render(request, 'admin/grading/enter.html', context)


@staff_member_required
def grading_results(request, exam_id):
    """İmtahan nəticələri cədvəli."""
    exam = get_object_or_404(Exam, pk=exam_id)
    student_exams = StudentExam.objects.filter(exam=exam).select_related('student__user').prefetch_related('answers__question')
    total_questions = exam.total_questions or exam.questions.filter(is_active=True).count()

    results = []
    buraxilis_map = {}
    if exam.dim_type == 'blok':
        buraxilis_map = _buraxilis_bal_map([se.student_id for se in student_exams])

    for se in student_exams:
        calc = _calc(se, total_questions)
        entry = {
            'student_exam': se,
            'student_name': se.student.user.get_full_name() or se.student.user.email,
            'student_id': se.student.student_id,
            'work_number': se.student.work_number,
            **calc,
        }
        if exam.dim_type == 'blok' and se.student_id in buraxilis_map:
            yekun = compute_yekun_bal(buraxilis_map[se.student_id], calc['nb_score'])
            entry['buraxilis_bal'] = float(yekun['buraxilis_bal'])
            entry['blok_bal'] = float(yekun['blok_bal'])
            entry['yekun_bal'] = float(yekun['yekun_bal'])
            entry['yekun_max_bal'] = float(yekun['max_bal'])
        results.append(entry)

    results.sort(key=lambda x: x['nb_score'], reverse=True)
    for i, r in enumerate(results):
        r['rank'] = i + 1

    dim_subject_names = []
    if results and results[0].get('is_dim'):
        dim_subject_names = [s['name'] for s in results[0]['dim_result']['per_subject']]

    avg_score = round(sum(r['nb_score'] for r in results) / len(results), 1) if results else 0

    context = {
        'title': f'{exam.title} — Nəticələr',
        'exam': exam,
        'results': results,
        'total_questions': total_questions,
        'dim_subject_names': dim_subject_names,
        'is_dim': bool(exam.dim_type),
        'avg_score': avg_score,
        'show_yekun': exam.dim_type == 'blok',
    }
    return render(request, 'admin/grading/results.html', context)


@staff_member_required
def grading_answer_card(request, student_exam_id):
    """Cavab kartı — yaşıl/qırmızı/boş vizual."""
    student_exam = get_object_or_404(
        StudentExam.objects.select_related('exam', 'student__user'),
        pk=student_exam_id
    )
    exam = student_exam.exam
    questions = exam.questions.filter(is_active=True).order_by('sort_order', 'created_at')

    answers_map = {}
    for sa in student_exam.answers.all():
        answers_map[sa.question_id] = sa

    cards = []
    for q in questions:
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

        if ea and selected:
            status = 'correct' if is_correct else 'wrong'
        elif ea and ea.text_answer:
            status = 'correct' if is_correct else 'wrong'
        else:
            status = 'empty'

        cards.append({
            'question': q,
            'number': q.question_number or q.sort_order or questions.index(q) + 1,
            'subject': q.subject,
            'status': status,
            'selected': selected,
            'correct_ids': correct_ids,
            'options': options,
            'answer': ea,
        })

    calc = _calc(student_exam, questions.count())

    # DİM imtahanları üçün fənn bölmələri
    subject_blocks = []
    if calc['is_dim']:
        by_subject = {}
        for c in cards:
            by_subject.setdefault(c['subject'] or '—', []).append(c)
        for s in calc['dim_result']['per_subject']:
            subject_blocks.append({
                'name': s['name'],
                'coeff': s['coeff'],
                'dq': s['dq'],
                'yq': s['yq'],
                'nb': s['nb'],
                'bal': s['bal'],
                'cards': by_subject.get(s['name'], []),
            })

    context = {
        'title': f'Cavab Kartı — {student_exam.student}',
        'student_exam': student_exam,
        'exam': exam,
        'cards': cards,
        'dq': calc['dq'],
        'yq': calc['yq'],
        'da': calc['da'],
        'empty': calc['empty'],
        'nb_score': calc['nb_score'],
        'total_questions': questions.count(),
        'is_dim': calc['is_dim'],
        'subject_blocks': subject_blocks,
        'dim_total_bal': calc['nb_score'],
        'dim_max_bal': float(calc['dim_result']['max_bal']) if calc['is_dim'] else 0,
    }
    return render(request, 'admin/grading/answer_card.html', context)
