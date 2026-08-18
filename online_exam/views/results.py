from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from ..models.results import SagirdResult
from ..serializers.results import SagirdResultSerializer, SagirdResultListSerializer


class SagirdResultViewSet(viewsets.ModelViewSet):
    queryset = SagirdResult.objects.all()
    filterset_fields = ["exam_id", "student_reg_number", "variant", "attempt_number"]
    search_fields = ["first_name", "last_name", "student_reg_number"]
    ordering_fields = ["total_point", "created_at"]

    def get_serializer_class(self):
        if self.action == "list":
            return SagirdResultListSerializer
        return SagirdResultSerializer

    @action(detail=True, methods=["get"], url_path="detail")
    def result_detail(self, request, pk=None):
        """Nəticə detallarını qaytarır (fənn üzrə ballar, sual detalları)."""
        result = self.get_object()
        return Response({
            "id": result.id,
            "exam_id": result.exam_id,
            "student_reg_number": result.student_reg_number,
            "first_name": result.first_name,
            "last_name": result.last_name,
            "variant": result.variant,
            "total_point": result.total_point,
            "result_compact": result.result,
            "result_details": result.result_details,
            "open_ended_scores": result.open_ended_scores,
        })

    @action(detail=True, methods=["post"], url_path="recalculate")
    def recalculate(self, request, pk=None):
        """Nəticəni yenidən hesabla."""
        from ..services.scoring import score_full_session
        from ..models.exam_core import CorrectAnswerKey

        result = self.get_object()

        # Cavab açarlarını seç
        answer_keys = CorrectAnswerKey.objects.filter(
            exam_id=result.exam_id,
            variant_name=result.variant,
        ).select_related("subject")

        # Seans cavablarını topla
        student_answers = {}
        if result.session:
            for sa in result.session.answers.all():
                if sa.subject not in student_answers:
                    student_answers[sa.subject] = {}
                student_answers[sa.subject][sa.question_number] = sa.answer

        if not student_answers:
            return Response(
                {"error": "Seans cavabları tapılmadı"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Yenidən hesabla
        scoring_result = score_full_session(
            answer_keys=answer_keys,
            student_answers_data=student_answers,
            is_online=True,
        )

        result.result = scoring_result["result_compact"]
        result.total_point = scoring_result["total_point"]
        result.result_details = scoring_result["result_details"]
        result.save(update_fields=["result", "total_point", "result_details", "updated_at"])

        return Response({
            "total_point": scoring_result["total_point"],
            "status": scoring_result["status"],
        })
