from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from ..models.markers import (
    Marker, QuestionAssignment, StudentAnswerGrading,
    IndividualGrade, MarkerAnswerGrade,
)
from ..serializers.markers import (
    MarkerSerializer, MarkerListSerializer,
    QuestionAssignmentSerializer, StudentAnswerGradingSerializer,
    IndividualGradeSerializer, MarkerAnswerGradeSerializer,
)
from ..services.marker_consensus import submit_grade, get_head_marker_queue


class MarkerViewSet(viewsets.ModelViewSet):
    queryset = Marker.objects.all()
    filterset_fields = ["role", "is_active"]
    search_fields = ["name", "email"]

    def get_serializer_class(self):
        if self.action == "list":
            return MarkerListSerializer
        return MarkerSerializer

    @action(detail=True, methods=["get"], url_path="queue")
    def marker_queue(self, request, pk=None):
        """
        Marker üçün gözləyən qiymətləndirmələri qaytarır.
        Blind grading: marker yalnız öz icazəli fənlərini görür.
        """
        marker = self.get_object()
        if marker.is_head_marker:
            gradings = get_head_marker_queue(marker)
        else:
            # Adi marker — pending/in_progress, öz fənləri
            allowed_subject_names = marker.allowed_subjects.values_list(
                "subject_name", flat=True
            )
            gradings = StudentAnswerGrading.objects.filter(
                status__in=[
                    StudentAnswerGrading.Status.PENDING,
                    StudentAnswerGrading.Status.IN_PROGRESS,
                ],
                subject_name__in=allowed_subject_names,
            ).select_related("result", "assignment").order_by("created_at")

        serializer = StudentAnswerGradingSerializer(gradings[:50], many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"], url_path="bulk-assign-questions")
    def bulk_assign_questions(self, request, pk=None):
        """
        Toplu sual təyini:
        {exam_id, subject_id, question_numbers: [...], required_marker_count}
        """
        marker = self.get_object()
        exam_id = request.data.get("exam_id")
        subject_id = request.data.get("subject_id")
        question_numbers = request.data.get("question_numbers", [])
        required_count = request.data.get("required_marker_count", 1)

        if not exam_id or not subject_id or not question_numbers:
            return Response(
                {"error": "exam_id, subject_id, question_numbers tələb olunur"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        created = 0
        for q_num in question_numbers:
            qa, _ = QuestionAssignment.objects.get_or_create(
                exam_id=exam_id,
                subject_id=subject_id,
                question_number=q_num,
                defaults={"required_marker_count": required_count},
            )
            qa.assigned_markers.add(marker)
            created += 1

        return Response({"assigned_count": created})


class QuestionAssignmentViewSet(viewsets.ModelViewSet):
    queryset = QuestionAssignment.objects.select_related(
        "exam", "subject", "head_marker",
    ).all()
    serializer_class = QuestionAssignmentSerializer
    filterset_fields = ["exam", "subject"]
    filter_horizontal = ["assigned_markers"]


class StudentAnswerGradingViewSet(viewsets.ModelViewSet):
    queryset = StudentAnswerGrading.objects.select_related(
        "result", "assignment",
    ).all()
    serializer_class = StudentAnswerGradingSerializer
    filterset_fields = ["status", "subject_name", "is_suspicious"]

    @action(detail=True, methods=["post"], url_path="submit-grade")
    def submit_marker_grade(self, request, pk=None):
        """
        Marker qiyməti təqdim edir.
        Body: {marker_id, fraction, is_suspicious, notes}
        """
        grading = self.get_object()
        marker_id = request.data.get("marker_id")
        fraction = request.data.get("fraction", "")
        is_suspicious = request.data.get("is_suspicious", False)
        notes = request.data.get("notes", "")

        if not marker_id:
            return Response(
                {"error": "marker_id tələb olunur"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            marker = Marker.objects.get(pk=marker_id)
        except Marker.DoesNotExist:
            return Response(
                {"error": "Marker tapılmadı"},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Maksimum ballı cavab açarından götür
        max_points = 0
        try:
            from ..models.exam_core import CorrectAnswerKey
            key = CorrectAnswerKey.objects.filter(
                exam=grading.assignment.exam,
                subject__subject_name=grading.subject_name,
            ).first()
            if key:
                for q in key.answers_data:
                    if q.get("question_number") == grading.question_number:
                        max_points = q.get("points", 0)
                        break
        except Exception:
            pass

        result = submit_grade(
            grading=grading,
            marker=marker,
            fraction_str=fraction,
            max_points=max_points,
            is_suspicious=is_suspicious,
            notes=notes,
        )

        return Response(result)


class IndividualGradeViewSet(viewsets.ModelViewSet):
    queryset = IndividualGrade.objects.select_related(
        "answer_grading", "marker",
    ).all()
    serializer_class = IndividualGradeSerializer
    filterset_fields = ["answer_grading", "marker"]


class MarkerAnswerGradeViewSet(viewsets.ModelViewSet):
    queryset = MarkerAnswerGrade.objects.all()
    serializer_class = MarkerAnswerGradeSerializer
    filterset_fields = ["subject_name"]
