from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from ..models.exam_core import Exam, CorrectAnswerKey, ExamSessions
from ..serializers.exam_core import (
    ExamSerializer, ExamListSerializer, CorrectAnswerKeySerializer, ExamSessionsSerializer,
)
from ..services.variant_selection import get_variant_choices, get_exam_online_state


class ExamViewSet(viewsets.ModelViewSet):
    queryset = Exam.objects.select_related("exam_type").all()
    filterset_fields = ["exam_date", "exam_type", "exam_register", "exam_result", "payment_type"]
    search_fields = ["exam_name"]
    ordering_fields = ["exam_date", "created_at"]

    def get_serializer_class(self):
        if self.action == "list":
            return ExamListSerializer
        return ExamSerializer

    @action(detail=True, methods=["get"], url_path="variants")
    def variants(self, request, pk=None):
        """Bu imtahanda mövcud variantları qaytarır."""
        variants = get_variant_choices(int(pk))
        return Response({"variants": variants})

    @action(detail=True, methods=["get"], url_path="online-state")
    def online_state(self, request, pk=None):
        """Bu online imtahanın cari vəziyyətini qaytarır."""
        state = get_exam_online_state(int(pk))
        return Response(state)

    @action(detail=True, methods=["get"], url_path="answer-keys")
    def answer_keys_list(self, request, pk=None):
        """Bu imtahana aid cavab açarlarının siyahısı."""
        keys = CorrectAnswerKey.objects.filter(exam_id=pk).select_related("subject")
        serializer = CorrectAnswerKeySerializer(keys, many=True)
        return Response(serializer.data)


class CorrectAnswerKeyViewSet(viewsets.ModelViewSet):
    queryset = CorrectAnswerKey.objects.select_related("exam", "subject").all()
    serializer_class = CorrectAnswerKeySerializer
    filterset_fields = ["exam", "subject", "variant_name", "is_online"]
    search_fields = ["variant_name"]

    @action(detail=False, methods=["post"], url_path="bulk-create")
    def bulk_create(self, request):
        """
        Toplu cavab açarı yaratma.
        Body: {"keys": [{exam, subject, variant_name, sinif, bolme, qrup, answers_data, ...}, ...]}
        """
        keys_data = request.data.get("keys", [])
        if not keys_data:
            return Response({"error": "keys siyahısı boşdur"}, status=status.HTTP_400_BAD_REQUEST)

        created = []
        for key_data in keys_data:
            serializer = CorrectAnswerKeySerializer(data=key_data)
            if serializer.is_valid():
                serializer.save()
                created.append(serializer.data)
            else:
                return Response(
                    {"error": serializer.errors, "data": key_data},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        return Response({"created": len(created), "keys": created}, status=status.HTTP_201_CREATED)


class ExamSessionsViewSet(viewsets.ModelViewSet):
    queryset = ExamSessions.objects.select_related("exam").all()
    serializer_class = ExamSessionsSerializer
    filterset_fields = ["exam"]
