from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone

from ..models.competition import (
    Competition, CompetitionQuestion, CompetitionParticipant,
    CompetitionQuestionAttempt,
)
from ..serializers.competition import (
    CompetitionSerializer, CompetitionQuestionSerializer,
    CompetitionParticipantSerializer, CompetitionQuestionAttemptSerializer,
)


class CompetitionViewSet(viewsets.ModelViewSet):
    queryset = Competition.objects.all()
    serializer_class = CompetitionSerializer
    filterset_fields = ["is_active"]
    search_fields = ["name"]

    @action(detail=True, methods=["post"], url_path="join")
    def join_competition(self, request, pk=None):
        """Müsabiqəyə qoşul."""
        competition = self.get_object()
        cabinet_id = request.data.get("cabinet_id")

        if not cabinet_id:
            return Response(
                {"error": "cabinet_id tələb olunur"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        now = timezone.now()
        if not competition.is_active:
            return Response(
                {"error": "Müsabiqə aktiv deyil"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if now < competition.start_datetime:
            return Response(
                {"error": "Müsabiqə hələ başlamayıb"},
                status=status.HTTP_403_FORBIDDEN,
            )
        if now > competition.deadline:
            return Response(
                {"error": "Müsabiqə artıq bitib"},
                status=status.HTTP_403_FORBIDDEN,
            )

        from ..models.cabinet import StudentCabinet
        try:
            cabinet = StudentCabinet.objects.get(pk=cabinet_id)
        except StudentCabinet.DoesNotExist:
            return Response(
                {"error": "Şagird kabineti tapılmadı"},
                status=status.HTTP_404_NOT_FOUND,
            )

        if not cabinet.is_course_student:
            return Response(
                {"error": "Yalnız kurs şagirdləri iştirak edə bilər"},
                status=status.HTTP_403_FORBIDDEN,
            )

        participant, created = CompetitionParticipant.objects.get_or_create(
            competition=competition,
            student=cabinet,
        )

        if not created:
            return Response(
                {"error": "Artıq qoşulmusunuz"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            CompetitionParticipantSerializer(participant).data,
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=["get"], url_path="leaderboard")
    def leaderboard(self, request, pk=None):
        """Liderlik lövhəsi — maskalanmış adlarla."""
        competition = self.get_object()
        participants = CompetitionParticipant.objects.filter(
            competition=competition
        ).order_by("-total_score", "total_answer_time_ms", "joined_at")

        result = []
        my_participant_id = request.query_params.get("participant_id")

        for i, p in enumerate(participants, 1):
            name = p.student.user.get_full_name() if p.student and p.student.user else "Naməlum"
            masked = _mask_name(name)

            entry = {
                "rank": i,
                "student_name": masked,
                "total_score": p.total_score,
                "total_answer_time_ms": p.total_answer_time_ms,
            }

            if str(p.pk) == str(my_participant_id):
                entry["is_me"] = True
                entry["student_name"] = name  # Tam ad

            result.append(entry)

        return Response({"leaderboard": result})

    @action(detail=True, methods=["get"], url_path="questions-list")
    def questions_list(self, request, pk=None):
        """Müsabiqə suallarını qaytarır (vaxt pəncərəsi ilə)."""
        competition = self.get_object()
        now = timezone.now()
        questions = CompetitionQuestion.objects.filter(
            competition=competition
        ).order_by("order")

        result = []
        for q in questions:
            is_active = q.start_datetime <= now <= q.end_datetime
            entry = {
                "id": q.id,
                "order": q.order,
                "points": q.points,
                "duration_seconds": q.duration_seconds,
                "question_input_type": q.question_input_type,
                "answer_type": q.answer_type,
                "answer_options": q.answer_options if is_active else [],
                "start_datetime": q.start_datetime.isoformat(),
                "end_datetime": q.end_datetime.isoformat(),
                "is_active": is_active,
            }
            result.append(entry)

        return Response({"questions": result})

    @action(detail=True, methods=["post"], url_path="start-question")
    def start_question(self, request, pk=None):
        """Sualı başlat — participant attempt yarat."""
        competition = self.get_object()
        participant_id = request.data.get("participant_id")
        question_id = request.data.get("question_id")

        if not participant_id or not question_id:
            return Response(
                {"error": "participant_id və question_id tələb olunur"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            participant = CompetitionParticipant.objects.get(
                pk=participant_id, competition=competition
            )
        except CompetitionParticipant.DoesNotExist:
            return Response(
                {"error": "İştirakçı tapılmadı"},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            question = CompetitionQuestion.objects.get(
                pk=question_id, competition=competition
            )
        except CompetitionQuestion.DoesNotExist:
            return Response(
                {"error": "Sual tapılmadı"},
                status=status.HTTP_404_NOT_FOUND,
            )

        now = timezone.now()
        if not (question.start_datetime <= now <= question.end_datetime):
            return Response(
                {"error": "Sual aktiv pəncərədə deyil"},
                status=status.HTTP_403_FORBIDDEN,
            )

        attempt, created = CompetitionQuestionAttempt.objects.get_or_create(
            participant=participant,
            question=question,
        )

        return Response(
            CompetitionQuestionAttemptSerializer(attempt).data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )

    @action(detail=True, methods=["post"], url_path="submit-answer")
    def submit_answer(self, request, pk=None):
        """Cavabı təqdim et."""
        competition = self.get_object()
        participant_id = request.data.get("participant_id")
        question_id = request.data.get("question_id")
        answer = request.data.get("answer", "")

        if not participant_id or not question_id:
            return Response(
                {"error": "participant_id və question_id tələb olunur"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            participant = CompetitionParticipant.objects.get(
                pk=participant_id, competition=competition
            )
        except CompetitionParticipant.DoesNotExist:
            return Response(
                {"error": "İştirakçı tapılmadı"},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            question = CompetitionQuestion.objects.get(
                pk=question_id, competition=competition
            )
        except CompetitionQuestion.DoesNotExist:
            return Response(
                {"error": "Sual tapılmadı"},
                status=status.HTTP_404_NOT_FOUND,
            )

        attempt = CompetitionQuestionAttempt.objects.filter(
            participant=participant, question=question
        ).first()

        if not attempt:
            return Response(
                {"error": "Öncə sualı başlatın"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        now = timezone.now()
        submitted_ms = int(now.timestamp() * 1000)

        attempt.answer = answer
        attempt.submitted_at_ms = submitted_ms

        # Vaxt yoxlaması
        started_ms = int(attempt.started_at.timestamp() * 1000)
        elapsed_ms = submitted_ms - started_ms
        if elapsed_ms > question.duration_seconds * 1000:
            attempt.is_timeout = True
            attempt.is_correct = False
            attempt.points_earned = 0
        else:
            # Qiymətləndirmə
            is_correct = _check_competition_answer(question, answer)
            attempt.is_correct = is_correct
            attempt.points_earned = question.points if is_correct else 0

        attempt.save()

        # Participant balını yenilə
        participant.total_score += attempt.points_earned
        participant.total_answer_time_ms += elapsed_ms
        participant.save(update_fields=["total_score", "total_answer_time_ms"])

        return Response({
            "is_correct": attempt.is_correct,
            "points_earned": float(attempt.points_earned),
            "is_timeout": attempt.is_timeout,
            "total_score": float(participant.total_score),
        })


class CompetitionQuestionViewSet(viewsets.ModelViewSet):
    queryset = CompetitionQuestion.objects.select_related("competition").all()
    serializer_class = CompetitionQuestionSerializer
    filterset_fields = ["competition"]


class CompetitionParticipantViewSet(viewsets.ModelViewSet):
    queryset = CompetitionParticipant.objects.select_related("competition", "student").all()
    serializer_class = CompetitionParticipantSerializer
    filterset_fields = ["competition", "student"]


class CompetitionQuestionAttemptViewSet(viewsets.ModelViewSet):
    queryset = CompetitionQuestionAttempt.objects.select_related("participant", "question").all()
    serializer_class = CompetitionQuestionAttemptSerializer
    filterset_fields = ["participant", "question"]


def _mask_name(name: str) -> str:
    """Adı maskala: Ka**** kimi."""
    if not name or len(name) < 2:
        return name
    parts = name.split()
    if len(parts) >= 2:
        first = parts[0][0] + "****"
        return f"{first}"
    return name[:2] + "****"


def _check_competition_answer(question: CompetitionQuestion, answer: str) -> bool:
    """Müsabiqə cavabını yoxla."""
    if not answer:
        return False

    correct = str(question.correct_answer).strip()
    student_ans = str(answer).strip()

    answer_type = question.answer_type

    if answer_type in ("qapalı",):
        # Bağlı — böyük hərf bərabərliyi
        return student_ans.upper() == correct.upper()
    elif answer_type == "uyğunlaşdırma":
        # Normallaşdırılmış müqayisə
        return student_ans.upper().replace(" ", "") == correct.upper().replace(" ", "")
    elif answer_type in ("açıq", "esse"):
        # Kiçik hərf string bərabərliyi
        return student_ans.lower() == correct.lower()
    else:
        return student_ans.upper() == correct.upper()
