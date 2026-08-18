from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.db import transaction

from ..models.cabinet import (
    StudentCabinet, ExamParticipation, ExamAttempt,
    OnlineExamAssignment, StudentExamSession, StudentAnswer,
)
from ..serializers.cabinet import (
    StudentCabinetSerializer, StudentCabinetListSerializer,
    ExamParticipationSerializer, ExamAttemptSerializer,
    OnlineExamAssignmentSerializer, StudentExamSessionSerializer,
    StudentAnswerSerializer,
)
from ..services.variant_selection import select_answer_keys, get_exam_online_state
from ..services.scoring import score_full_session


class StudentCabinetViewSet(viewsets.ModelViewSet):
    queryset = StudentCabinet.objects.select_related("user").all()
    filterset_fields = ["is_active", "is_course_student", "student_verification_status"]
    search_fields = ["work_number", "phone", "user__first_name", "user__last_name"]

    def get_serializer_class(self):
        if self.action == "list":
            return StudentCabinetListSerializer
        return StudentCabinetSerializer

    @action(detail=True, methods=["get"], url_path="exams")
    def student_exams(self, request, pk=None):
        """Şagirdin imtahanlarını qaytarır."""
        cabinet = self.get_object()
        assignments = OnlineExamAssignment.objects.filter(
            student=cabinet, is_visible=True, is_quiz=False
        )
        serializer = OnlineExamAssignmentSerializer(assignments, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"], url_path="quizzes")
    def student_quizzes(self, request, pk=None):
        """Şagirdin quizlərini qaytarır."""
        cabinet = self.get_object()
        assignments = OnlineExamAssignment.objects.filter(
            student=cabinet, is_visible=True, is_quiz=True
        )
        serializer = OnlineExamAssignmentSerializer(assignments, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"], url_path="results")
    def student_results(self, request, pk=None):
        """Şagirdin nəticələrini qaytarır."""
        from ..models.results import SagirdResult
        cabinet = self.get_object()
        results = SagirdResult.objects.filter(cabinet=cabinet)
        from ..serializers.results import SagirdResultListSerializer
        serializer = SagirdResultListSerializer(results, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"], url_path="notifications")
    def student_notifications(self, request, pk=None):
        """Şagirdin bildirişlərini qaytarır."""
        from ..models.notifications import CabinetNotification
        cabinet = self.get_object()
        notifications = CabinetNotification.objects.filter(student=cabinet)[:20]
        from ..serializers.notifications import CabinetNotificationSerializer
        serializer = CabinetNotificationSerializer(notifications, many=True)
        return Response(serializer.data)


class ExamParticipationViewSet(viewsets.ModelViewSet):
    queryset = ExamParticipation.objects.select_related("student", "exam").all()
    serializer_class = ExamParticipationSerializer
    filterset_fields = ["student", "exam", "is_quiz", "status"]


class OnlineExamAssignmentViewSet(viewsets.ModelViewSet):
    queryset = OnlineExamAssignment.objects.select_related(
        "student", "sinif", "bolme", "qrup", "register", "participation", "sagird_result",
    ).all()
    serializer_class = OnlineExamAssignmentSerializer
    filterset_fields = ["student", "exam_id", "status", "is_quiz", "variant_name"]

    @action(detail=True, methods=["get"], url_path="start")
    def start_exam(self, request, pk=None):
        """
        İmtahanı başlat — seans yarat.
        Bölmə 5.5: Təyinat kilidi, yoxlamalar, lazy enrollment.
        """
        assignment = self.get_object()

        # Yoxlamalar
        if assignment.status != OnlineExamAssignment.Status.ACTIVE:
            return Response(
                {"error": "Təyinat aktiv deyil"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Hazırlıq taymeri yoxlaması
        if not assignment.prep_timer_completed:
            return Response(
                {"error": "Hazırlıq taymeri hələ bitməyib"},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Online cədvəl pəncərəsi yoxlaması
        state = get_exam_online_state(assignment.exam_id)
        now = timezone.now()
        if state["state"] == "upcoming":
            return Response(
                {"error": "İmtahan hələ başlamayıb"},
                status=status.HTTP_403_FORBIDDEN,
            )
        if state["state"] == "ended":
            return Response(
                {"error": "İmtahan artıq bitib"},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Resume: mövcud seans varsa onu qaytar
        existing_session = StudentExamSession.objects.filter(
            assignment=assignment
        ).first()

        if existing_session:
            return Response(StudentExamSessionSerializer(existing_session).data)

        # Lazy enrollment — ExamParticipation yarat
        participation, _ = ExamParticipation.objects.get_or_create(
            student=assignment.student,
            exam_id=assignment.exam_id,
            is_quiz=assignment.is_quiz,
            defaults={
                "register": assignment.register,
                "status": ExamParticipation.Status.ACTIVE,
                "is_online": True,
                "exam_name": assignment.exam_name,
                "exam_date": assignment.exam_date,
            },
        )
        participation.attempt_count += 1
        participation.last_attempt_number = assignment.attempt_number
        participation.last_attempt_type = "online"
        participation.last_attempt_at = now
        participation.save(update_fields=[
            "attempt_count", "last_attempt_number", "last_attempt_type",
            "last_attempt_at",
        ])

        # Seans yarat
        with transaction.atomic():
            session = StudentExamSession.objects.create(
                assignment=assignment,
            )
            assignment.participation = participation
            assignment.save(update_fields=["participation"])

        return Response(StudentExamSessionSerializer(session).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["get"], url_path="questions")
    def get_questions(self, request, pk=None):
        """
        Sualları qaytar — variant seçim alqoritmi ilə.
        Bölmə 5.6: Variant seçim alqoritmi ilə suallar yığılır, hamısı bir dəfəyə göndərilir.
        """
        assignment = self.get_object()

        # Seans yoxlaması
        session = StudentExamSession.objects.filter(assignment=assignment).first()
        if not session:
            return Response(
                {"error": "İmtahan başladılmayıb"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Variant seçim alqoritmi
        sinif_id = assignment.sinif_id
        bolme_id = assignment.bolme_id
        qrup_id = assignment.qrup_id
        variant = assignment.variant_name or None

        answer_keys = select_answer_keys(
            exam_id=assignment.exam_id,
            variant_name=variant,
            sinif_id=sinif_id,
            bolme_id=bolme_id,
            qrup_id=qrup_id,
        )

        # Sualları topla
        questions = []
        question_counter = 1
        for key in answer_keys:
            subject = key.subject.subject_name
            for q_data in (key.answers_data or []):
                questions.append({
                    "id": f"{key.key_id}_{question_counter}",
                    "question_number": question_counter,
                    "original_question_number": q_data.get("question_number", question_counter),
                    "question_text": q_data.get("question_text", ""),
                    "question_image": q_data.get("question_image", ""),
                    "audio_url": q_data.get("audio_url", ""),
                    "question_type": q_data.get("question_type", "Qapalı"),
                    "subject": subject,
                    "is_choice": q_data.get("is_choice", False),
                    "is_starred": q_data.get("is_starred", False),
                    "points": q_data.get("points", 0),
                    "marker_check": q_data.get("marker_check", False),
                })
                question_counter += 1

        return Response({
            "assignment_id": assignment.id,
            "exam_name": assignment.exam_name,
            "variant": assignment.variant_name,
            "duration_minutes": assignment.duration_minutes,
            "session_started_at": session.started_at.isoformat() if session.started_at else None,
            "total_questions": len(questions),
            "questions": questions,
        })

    @action(detail=True, methods=["post"], url_path="save-answer")
    def save_answer(self, request, pk=None):
        """
        Cavabı yadda saxla (autosave).
        Hər cavab ayrıca upsert olunur (progressiv autosave).
        """
        assignment = self.get_object()
        session = StudentExamSession.objects.filter(
            assignment=assignment, is_submitted=False
        ).first()

        if not session:
            return Response(
                {"error": "Aktiv seans tapılmadı"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        question_number = request.data.get("question_number")
        subject = request.data.get("subject", "")
        question_type = request.data.get("question_type", "")
        answer = request.data.get("answer", "")

        if question_number is None:
            return Response(
                {"error": "question_number tələb olunur"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Upsert
        student_answer, created = StudentAnswer.objects.update_or_create(
            session=session,
            question_number=question_number,
            subject=subject,
            defaults={
                "question_type": question_type,
                "answer": answer,
            },
        )

        return Response({
            "saved": True,
            "question_number": question_number,
            "created": created,
        })

    @action(detail=True, methods=["post"], url_path="submit")
    def submit_exam(self, request, pk=None):
        """
        İmtahanı təqdim et → qiymətləndirmə.
        Bölmə 5.10: Seans kilidi, finalize_session_submission.
        """
        assignment = self.get_object()
        session = StudentExamSession.objects.filter(
            assignment=assignment, is_submitted=False
        ).first()

        if not session:
            return Response(
                {"error": "Təqdim ediləcək seans tapılmadı (artıq təqdim olunub?)"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        with transaction.atomic():
            # Seansı təqdim et
            session.is_submitted = True
            session.submitted_at = timezone.now()
            session.save(update_fields=["is_submitted", "submitted_at"])

            # Təyinatı tamamla
            assignment.status = OnlineExamAssignment.Status.SUBMITTED
            assignment.save(update_fields=["status"])

            # Cavabları topla
            student_answers = {}
            for sa in session.answers.all():
                if sa.subject not in student_answers:
                    student_answers[sa.subject] = {}
                student_answers[sa.subject][sa.question_number] = sa.answer

            # Cavab açarlarını seç
            answer_keys = select_answer_keys(
                exam_id=assignment.exam_id,
                variant_name=assignment.variant_name or None,
                sinif_id=assignment.sinif_id,
                bolme_id=assignment.bolme_id,
                qrup_id=assignment.qrup_id,
            )

            # Qiymətləndirmə
            scoring_result = score_full_session(
                answer_keys=answer_keys,
                student_answers_data=student_answers,
                is_online=True,
            )

            # SagirdResult yarat/yenilə
            from ..models.results import SagirdResult

            result, _ = SagirdResult.objects.update_or_create(
                cabinet=assignment.student,
                exam_id=assignment.exam_id,
                attempt_number=assignment.attempt_number,
                defaults={
                    "student_id": assignment.register_id or 0,
                    "student_reg_number": str(assignment.student.work_number),
                    "first_name": assignment.student.user.first_name,
                    "last_name": assignment.student.user.last_name,
                    "sinif": assignment.sinif.sinif_name if assignment.sinif else "",
                    "variant": assignment.variant_name,
                    "bolme": assignment.bolme.bolme_name if assignment.bolme else "",
                    "qrup": assignment.qrup.qrup_name if assignment.qrup else "",
                    "session": session,
                    "result": scoring_result["result_compact"],
                    "total_point": scoring_result["total_point"],
                    "result_details": scoring_result["result_details"],
                },
            )

            session.result = result
            session.save(update_fields=["result"])
            assignment.sagird_result = result
            assignment.result_generated_at = timezone.now()
            assignment.save(update_fields=["sagird_result", "result_generated_at"])

            # Participation yenilə
            if assignment.participation:
                assignment.participation.score = scoring_result["total_point"]
                assignment.participation.status = ExamParticipation.Status.COMPLETED
                assignment.participation.save(update_fields=["score", "status"])

            # Açıq suallar üçün grading yarat
            from ..services.marker_consensus import create_answer_gradings_for_session
            create_answer_gradings_for_session(session)

        return Response({
            "total_point": scoring_result["total_point"],
            "is_manual_check_pending": scoring_result["is_manual_check_pending"],
            "status": scoring_result["status"],
            "detail_url": f"/api/v1/online-exam/results/{result.id}/",
        })


class StudentExamSessionViewSet(viewsets.ModelViewSet):
    queryset = StudentExamSession.objects.select_related("assignment", "result").all()
    serializer_class = StudentExamSessionSerializer
    filterset_fields = ["assignment", "is_submitted"]


class StudentAnswerViewSet(viewsets.ModelViewSet):
    queryset = StudentAnswer.objects.select_related("session").all()
    serializer_class = StudentAnswerSerializer
    filterset_fields = ["session", "question_number", "subject"]
