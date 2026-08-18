import uuid
from datetime import datetime
from decimal import Decimal
from zoneinfo import ZoneInfo
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.utils.text import slugify

from exam_system.models import Exam, Question
from courses.models import Exam as PublicExam
from exam_system.dim import (
    SUBJECT_PLANS,
    BURAXILIS_SUBJECTS,
    ANSWER_OPTIONS,
    QUESTIONS_PER_SUBJECT,
    BLOK_STRUCTURE,
    get_subjects,
    get_buraxilis_structure,
)


BAKU_TZ = ZoneInfo('Asia/Baku')


def _parse_datetime(value):
    """Daxil edilən tarixi Azərbaycan saat qurşağında (Asia/Baku) təfsir edir."""
    if not value:
        return None
    try:
        dt = datetime.fromisoformat(value)
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=BAKU_TZ)
    else:
        dt = dt.astimezone(BAKU_TZ)
    return dt


def _sync_public_exam(dim_exam):
    """DİM imtahanını saytda göstərmək üçün əlaqəli 'Sınaq imtahanı' yaradır/yeniləyir."""
    if not dim_exam.start_datetime:
        return None
    deadline = dim_exam.registration_deadline or dim_exam.start_datetime
    public, created = PublicExam.objects.get_or_create(
        slug=dim_exam.slug,
        defaults={
            'title': dim_exam.title,
            'description': dim_exam.description,
            'date': dim_exam.start_datetime,
            'registration_deadline': deadline,
            'price': dim_exam.price,
            'location': dim_exam.location,
            'max_participants': dim_exam.max_participants,
            'is_active': dim_exam.is_active,
        },
    )
    if not created:
        PublicExam.objects.filter(pk=public.pk).update(
            title=dim_exam.title,
            description=dim_exam.description,
            date=dim_exam.start_datetime,
            registration_deadline=deadline,
            price=dim_exam.price,
            location=dim_exam.location,
            max_participants=dim_exam.max_participants,
            is_active=dim_exam.is_active,
        )
    return public


@staff_member_required
def dim_exam_list(request):
    """İmtahanlar — DİM imtahanı yarat, düzgün cavabları daxil et, sil."""
    exams = Exam.objects.select_related().order_by('-start_datetime', '-created_at')

    public_slugs = {e.slug for e in exams}
    public_by_slug = {
        p.slug: p for p in PublicExam.objects.filter(slug__in=public_slugs).only('id', 'slug')
    }
    for e in exams:
        pub = public_by_slug.get(e.slug)
        e.registrations_count = pub.registrations.count() if pub else 0

    if request.method == 'POST':
        action = request.POST.get('action', '')
        if action == 'create_exam':
            title = request.POST.get('title', '').strip()
            start_datetime = request.POST.get('start_datetime', '').strip()
            registration_deadline = request.POST.get('registration_deadline', '').strip()
            dim_type = request.POST.get('dim_type', 'blok')
            exam_group = request.POST.get('exam_group', '1')
            group_subtype = request.POST.get('group_subtype', '')
            price = request.POST.get('price', '').strip()
            location = request.POST.get('location', '').strip()
            max_participants = request.POST.get('max_participants', '').strip()

            if not title:
                messages.error(request, 'İmtahan adı mütləqdir.')
                return redirect('dim_exam_list')

            if dim_type == 'buraxilis':
                # Buraxılış imtahanı sabit fənndir: Riyaziyyat + Azərbaycan dili + Xarici dil.
                exam_group = ''
                group_subtype = ''
                subject_plan = BURAXILIS_SUBJECTS
            else:
                plan = SUBJECT_PLANS.get(exam_group, {})
                if group_subtype not in plan:
                    group_subtype = list(plan.keys())[0] if plan else ''
                subject_plan = plan.get(group_subtype, [])

            max_score = Decimal('300') if dim_type == 'buraxilis' else Decimal('400')

            if dim_type == 'buraxilis':
                total_questions = sum(
                    sum(b['count'] for b in item['blocks'])
                    for item in get_buraxilis_structure()
                )
            else:
                total_questions = len(subject_plan) * QUESTIONS_PER_SUBJECT

            exam = Exam.objects.create(
                title=title,
                slug=slugify(title) + '-' + uuid.uuid4().hex[:6],
                exam_type='entrance' if dim_type == 'blok' else 'course',
                status='draft',
                dim_type=dim_type,
                exam_group=exam_group,
                group_subtype=group_subtype,
                total_questions=total_questions,
                max_score=max_score,
                start_datetime=_parse_datetime(start_datetime),
                registration_deadline=_parse_datetime(registration_deadline),
                price=Decimal(price or '0'),
                location=location,
                max_participants=int(max_participants or 0),
                is_active=True,
                created_by=request.user,
            )

            _create_dim_questions(exam, subject_plan)
            _sync_public_exam(exam)

            subjects = [item['subject'] for item in get_subjects(exam)]
            messages.success(
                request,
                f'"{exam.title}" yaradıldı ({", ".join(subjects) or "fənlər təyin edilməyib"}). '
                f'İmtahan saytda görünür, qeydiyyat sonu: {exam.registration_deadline.strftime("%d.%m.%Y %H:%M") if exam.registration_deadline else "təyin edilməyib"}. '
                f'İndi düzgün cavabları daxil edin.'
            )
            return redirect('dim_exam_answers', exam_id=exam.pk)

        elif action == 'delete_exam':
            exam_id = request.POST.get('exam_id')
            exam = Exam.objects.filter(pk=exam_id).first()
            if exam:
                PublicExam.objects.filter(slug=exam.slug).delete()
                messages.warning(request, f'"{exam.title}" silindi.')
                exam.delete()
            return redirect('dim_exam_list')

    context = {
        'title': 'İmtahanlar',
        'exams': exams,
        'subject_plans': SUBJECT_PLANS,
        'answer_options': ANSWER_OPTIONS,
        'questions_per_subject': QUESTIONS_PER_SUBJECT,
        'now_value': timezone.localtime(timezone.now()).strftime('%Y-%m-%dT%H:%M'),
    }
    return render(request, 'admin/exams/list.html', context)


@staff_member_required
def dim_exam_registrations(request, exam_id):
    """DİM imtahanına ictimai formadan qeydiyyatdan keçənlərin siyahısı."""
    exam = get_object_or_404(Exam, pk=exam_id)
    public = PublicExam.objects.filter(slug=exam.slug).first()
    registrations = public.registrations.all() if public else PublicExam.objects.none()
    context = {
        'title': 'Qeydiyyatlar',
        'exam': exam,
        'public': public,
        'registrations': registrations,
        'total': registrations.count(),
    }
    return render(request, 'admin/exams/registrations.html', context)


def _create_dim_questions(exam, subject_plan):
    """DİM imtahanı üçün avtomatik sual səbətləri yaradır.

    Buraxılış: hər fənn üçün blok strukturuna uyğun (qapalı / kodlaşdırılan açıq / tam açıq).
    Blok: hər fənn 30 sual (hamısı A–E seçimli).
    """
    existing = Question.objects.filter(exam=exam).count()
    if existing:
        return
    questions = []

    if exam.dim_type == 'buraxilis':
        for s_idx, item in enumerate(get_buraxilis_structure()):
            subject_name = item['subject']
            number = 0
            for block in item['blocks']:
                qtype = block['type']
                points = block['points']
                for _ in range(block['count']):
                    number += 1
                    if qtype == 'qapali':
                        questions.append(
                            Question(
                                exam=exam,
                                question_type='single_choice',
                                text=f'{subject_name} — {number}. sual',
                                subject=subject_name,
                                question_number=number,
                                sort_order=s_idx * 100 + number,
                                points=points,
                                answers_data={
                                    'options': [{'id': letter, 'text': letter} for letter in ANSWER_OPTIONS],
                                    'correct': None,
                                    'grading': 'auto',
                                },
                            )
                        )
                    elif qtype == 'kodlasdirilan':
                        questions.append(
                            Question(
                                exam=exam,
                                question_type='text',
                                text=f'{subject_name} — {number}. sual',
                                subject=subject_name,
                                question_number=number,
                                sort_order=s_idx * 100 + number,
                                points=points,
                                answers_data={
                                    'correct_text': '',
                                    'grading': 'fixed',
                                },
                            )
                        )
                    else:  # 'aciq'
                        questions.append(
                            Question(
                                exam=exam,
                                question_type='text',
                                text=f'{subject_name} — {number}. sual',
                                subject=subject_name,
                                question_number=number,
                                sort_order=s_idx * 100 + number,
                                points=points,
                                answers_data={
                                    'grading': 'coefficient',
                                },
                            )
                        )
        Question.objects.bulk_create(questions)
        return

    for s_idx, item in enumerate(subject_plan):
        subject_name = item['subject']
        number = 0
        for block in BLOK_STRUCTURE:
            qtype = block['type']
            points = block['points']
            for _ in range(block['count']):
                number += 1
                if qtype == 'qapali':
                    questions.append(
                        Question(
                            exam=exam,
                            question_type='single_choice',
                            text=f'{subject_name} — {number}. sual',
                            subject=subject_name,
                            question_number=number,
                            sort_order=s_idx * 100 + number,
                            points=points,
                            answers_data={
                                'options': [{'id': letter, 'text': letter} for letter in ANSWER_OPTIONS],
                                'correct': None,
                                'grading': 'auto',
                            },
                        )
                    )
                elif qtype == 'kodlasdirilan':
                    questions.append(
                        Question(
                            exam=exam,
                            question_type='text',
                            text=f'{subject_name} — {number}. sual',
                            subject=subject_name,
                            question_number=number,
                            sort_order=s_idx * 100 + number,
                            points=points,
                            answers_data={
                                'correct_text': '',
                                'grading': 'fixed',
                            },
                        )
                    )
                else:  # 'aciq' — tam açıq sual
                    questions.append(
                        Question(
                            exam=exam,
                            question_type='text',
                            text=f'{subject_name} — {number}. sual',
                            subject=subject_name,
                            question_number=number,
                            sort_order=s_idx * 100 + number,
                            points=points,
                            answers_data={
                                'grading': 'coefficient',
                            },
                        )
                    )
    Question.objects.bulk_create(questions)


@staff_member_required
def dim_exam_answers(request, exam_id):
    """DİM imtahanının düzgün cavablarını daxil et (3 fənn x 30 sual, A–E)."""
    exam = get_object_or_404(Exam, pk=exam_id)
    questions = exam.questions.filter(is_active=True).order_by('sort_order', 'created_at')

    if request.method == 'POST':
        saved = 0
        for q in questions:
            grading = (q.answers_data or {}).get('grading') or 'auto'
            data = dict(q.answers_data or {})
            if grading == 'coefficient':
                continue
            if grading == 'fixed':
                text_val = request.POST.get(f'q_{q.pk}_correct', '').strip()
                data['correct_text'] = text_val
                if text_val:
                    saved += 1
                q.answers_data = data
                q.save(update_fields=['answers_data'])
                continue
            letter = request.POST.get(f'q_{q.pk}', '').strip().upper()
            text_val = request.POST.get(f'q_{q.pk}_text', '').strip()
            if letter in ANSWER_OPTIONS:
                data['correct'] = letter
                saved += 1
            else:
                data['correct'] = None
            q.answers_data = data
            if text_val:
                q.text = text_val
            q.save(update_fields=['answers_data', 'text'])
        messages.success(request, f'{saved} düzgün cavab qeyd edildi.')
        return redirect('dim_exam_answers', exam_id=exam.pk)

    subjects = get_subjects(exam)
    subject_blocks = []
    for s_idx, item in enumerate(subjects):
        subject_name = item['subject']
        coeff = item['weight']
        subj_qs = [q for q in questions if q.subject == subject_name]
        subj_qs.sort(key=lambda q: (q.question_number or q.sort_order))
        for q in subj_qs:
            qd = q.answers_data or {}
            q.current_correct = qd.get('correct') or ''
            q.current_correct_text = qd.get('correct_text') or ''
            q.grading_method = qd.get('grading') or 'auto'
        subject_blocks.append({
            'name': subject_name,
            'coeff': coeff,
            'weight': coeff,
            'questions': subj_qs,
            'index': s_idx,
        })

    answered = sum(
        1 for q in questions
        if (q.answers_data or {}).get('correct') or (q.answers_data or {}).get('correct_text')
    )

    context = {
        'title': f'{exam.title} — Düzgün Cavablar',
        'exam': exam,
        'subject_blocks': subject_blocks,
        'answer_options': ANSWER_OPTIONS,
        'answered': answered,
        'total': questions.count(),
    }
    return render(request, 'admin/exams/answers.html', context)


@staff_member_required
@require_POST
def dim_exam_delete(request, exam_id):
    exam = get_object_or_404(Exam, pk=exam_id)
    title = exam.title
    PublicExam.objects.filter(slug=exam.slug).delete()
    exam.delete()
    messages.warning(request, f'"{title}" silindi.')
    return redirect('dim_exam_list')
