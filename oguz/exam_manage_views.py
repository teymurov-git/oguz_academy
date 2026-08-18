import json
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Sum
from decimal import Decimal

from exam_system.models import Exam, Question, StudentExam, StudentAnswer


def _is_teacher(user):
    if hasattr(user, 'teacher_profile'):
        return True
    from roles.models import UserRole
    return UserRole.objects.filter(user=user, role__slug='muellim').exists()


@staff_member_required
def exam_manage(request, exam_id):
    """İmtahan suallarını + düzgün cavabları idarə et."""
    exam = get_object_or_404(Exam, pk=exam_id)
    questions = exam.questions.filter(is_active=True).order_by('sort_order', 'created_at')

    q_data = []
    for q in questions:
        options = q.answers_data.get('options', [])
        correct_ids = [o['id'] for o in options if o.get('is_correct')]
        q_data.append({
            'question': q,
            'options': options,
            'correct_ids': correct_ids,
        })

    total_points = questions.aggregate(Sum('points'))['points__sum'] or 0

    context = {
        'title': f'{exam.title} — Suallar',
        'exam': exam,
        'questions': q_data,
        'total_points': total_points,
    }
    return render(request, 'admin/exam_manage.html', context)


@staff_member_required
@require_POST
def exam_question_add(request, exam_id):
    """Yeni sual əlavə et."""
    exam = get_object_or_404(Exam, pk=exam_id)
    qtype = request.POST.get('question_type', 'single_choice')
    text = request.POST.get('text', '').strip()
    points = request.POST.get('points', '1').strip()
    sort_order = request.POST.get('sort_order', '0').strip()

    if not text:
        return redirect('exam_manage', exam_id=exam.pk)

    options = []
    option_count = int(request.POST.get('option_count', 0))
    for i in range(option_count):
        oid = request.POST.get(f'option_{i}_id', '').strip()
        otext = request.POST.get(f'option_{i}_text', '').strip()
        ocorrect = request.POST.get(f'option_{i}_correct') == 'on'
        if oid and otext:
            options.append({
                'id': oid,
                'text': otext,
                'is_correct': ocorrect,
            })

    correct_text = request.POST.get('correct_text', '').strip()

    q = Question.objects.create(
        exam=exam,
        question_type=qtype,
        text=text,
        answers_data={
            'options': options,
            'correct_text': correct_text,
        },
        points=Decimal(points) if points else Decimal('1'),
        sort_order=int(sort_order) if sort_order else 0,
    )

    return redirect('exam_manage', exam_id=exam.pk)


@staff_member_required
@require_POST
def exam_question_edit(request, exam_id, question_id):
    """Suali redaktə et."""
    exam = get_object_or_404(Exam, pk=exam_id)
    question = get_object_or_404(Question, pk=question_id, exam=exam)

    question.question_type = request.POST.get('question_type', question.question_type)
    question.text = request.POST.get('text', question.text).strip()
    question.points = Decimal(request.POST.get('points', str(question.points)))
    question.sort_order = int(request.POST.get('sort_order', question.sort_order))

    options = []
    option_count = int(request.POST.get('option_count', 0))
    for i in range(option_count):
        oid = request.POST.get(f'option_{i}_id', '').strip()
        otext = request.POST.get(f'option_{i}_text', '').strip()
        ocorrect = request.POST.get(f'option_{i}_correct') == 'on'
        if oid and otext:
            options.append({
                'id': oid,
                'text': otext,
                'is_correct': ocorrect,
            })

    correct_text = request.POST.get('correct_text', '').strip()
    question.answers_data = {
        'options': options,
        'correct_text': correct_text,
    }
    question.save()

    return redirect('exam_manage', exam_id=exam.pk)


@staff_member_required
@require_POST
def exam_question_delete(request, exam_id, question_id):
    """Sualı sil."""
    exam = get_object_or_404(Exam, pk=exam_id)
    question = get_object_or_404(Question, pk=question_id, exam=exam)
    question.delete()
    return redirect('exam_manage', exam_id=exam.pk)


@staff_member_required
@require_POST
def exam_question_reorder(request, exam_id):
    """Sıralamanı yenilə."""
    exam = get_object_or_404(Exam, pk=exam_id)
    orders = request.POST.get('orders', '')
    if orders:
        for pair in orders.split(','):
            parts = pair.split(':')
            if len(parts) == 2:
                qid, order = parts[0].strip(), parts[1].strip()
                try:
                    Question.objects.filter(pk=qid, exam=exam).update(sort_order=int(order))
                except (ValueError, Exception):
                    pass
    return JsonResponse({'ok': True})
