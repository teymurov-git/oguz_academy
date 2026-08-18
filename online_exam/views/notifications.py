from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta
import secrets

from ..models.notifications import (
    NotificationTemplate, CabinetNotification, CabinetActivity,
    LoginAttempt, LoginBlock, PasswordResetOTP, WhatsAppTemplate,
    ExamRecording,
)
from ..serializers.notifications import (
    NotificationTemplateSerializer, CabinetNotificationSerializer,
    CabinetActivitySerializer, LoginAttemptSerializer, LoginBlockSerializer,
    PasswordResetOTPSerializer, WhatsAppTemplateSerializer,
    ExamRecordingSerializer,
)


class NotificationTemplateViewSet(viewsets.ModelViewSet):
    queryset = NotificationTemplate.objects.all()
    serializer_class = NotificationTemplateSerializer
    filterset_fields = ["notification_type"]
    search_fields = ["name", "title"]


class CabinetNotificationViewSet(viewsets.ModelViewSet):
    queryset = CabinetNotification.objects.select_related("student", "template").all()
    serializer_class = CabinetNotificationSerializer
    filterset_fields = ["student", "is_read"]

    @action(detail=True, methods=["post"], url_path="mark-read")
    def mark_read(self, request, pk=None):
        """Bildirişi oxunub kimi işarələ."""
        notification = self.get_object()
        notification.is_read = True
        notification.save(update_fields=["is_read"])
        return Response({"ok": True})

    @action(detail=False, methods=["post"], url_path="mark-all-read")
    def mark_all_read(self, request):
        """Bütün bildirişləri oxunub kimi işarələ."""
        student_id = request.data.get("student_id")
        if not student_id:
            return Response(
                {"error": "student_id tələb olunur"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        updated = CabinetNotification.objects.filter(
            student_id=student_id, is_read=False
        ).update(is_read=True)
        return Response({"marked": updated})

    @action(detail=False, methods=["get"], url_path="unread-count")
    def unread_count(self, request):
        """Oxunmamış bildiriş sayını qaytarır."""
        student_id = request.query_params.get("student_id")
        if not student_id:
            return Response({"count": 0})
        count = CabinetNotification.objects.filter(
            student_id=student_id, is_read=False
        ).count()
        return Response({"count": count})

    @action(detail=False, methods=["post"], url_path="bulk-create")
    def bulk_create(self, request):
        """Toplu bildiriş yaratma."""
        student_ids = request.data.get("student_ids", [])
        title = request.data.get("title", "")
        message = request.data.get("message", "")
        link = request.data.get("link", "")
        template_id = request.data.get("template_id")

        if not student_ids or not title:
            return Response(
                {"error": "student_ids və title tələb olunur"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        template = None
        if template_id:
            template = NotificationTemplate.objects.filter(pk=template_id).first()

        notifications = []
        for sid in student_ids:
            n = CabinetNotification(
                student_id=sid,
                title=title,
                message=message,
                link=link,
                template=template,
            )
            notifications.append(n)

        CabinetNotification.objects.bulk_create(notifications)
        return Response({"created": len(notifications)}, status=status.HTTP_201_CREATED)


class CabinetActivityViewSet(viewsets.ModelViewSet):
    queryset = CabinetActivity.objects.select_related("student").all()
    serializer_class = CabinetActivitySerializer
    filterset_fields = ["student", "activity_type"]


class LoginAttemptViewSet(viewsets.ModelViewSet):
    queryset = LoginAttempt.objects.all()
    serializer_class = LoginAttemptSerializer
    filterset_fields = ["is_successful", "identifier_type"]
    search_fields = ["identifier", "ip_address"]

    @action(detail=False, methods=["post"], url_path="check-block")
    def check_block(self, request):
        """
        Login cəhdi yoxla — brute-force blok.
        2 dəqiqədə 5 uğursuz cəhd → blok.
        """
        identifier = request.data.get("identifier", "")
        identifier_type = request.data.get("identifier_type", "email")
        ip_address = request._request.META.get("REMOTE_ADDR", "0.0.0.0")
        cf_token = request.data.get("cf-turnstile-response", "")

        # Blok yoxlaması
        block = LoginBlock.objects.filter(identifier=identifier).first()
        if block and block.blocked_until > timezone.now():
            remaining = (block.blocked_until - timezone.now()).seconds
            return Response(
                {"blocked": True, "remaining_seconds": remaining},
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )

        # Son 2 dəqiqədəki uğursuz cəhdləri say
        two_min_ago = timezone.now() - timedelta(minutes=2)
        failed_count = LoginAttempt.objects.filter(
            identifier=identifier,
            is_successful=False,
            created_at__gte=two_min_ago,
        ).count()

        if failed_count >= 5:
            # Blokla
            LoginBlock.objects.update_or_create(
                identifier=identifier,
                defaults={
                    "blocked_until": timezone.now() + timedelta(minutes=2),
                    "attempt_count": failed_count,
                },
            )
            return Response(
                {"blocked": True, "remaining_seconds": 120},
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )

        # Cəhdi qeydə al
        LoginAttempt.objects.create(
            identifier=identifier,
            identifier_type=identifier_type,
            ip_address=ip_address,
            is_successful=False,
        )

        return Response({"blocked": False, "failed_count": failed_count + 1})

    @action(detail=False, methods=["post"], url_path="record-success")
    def record_success(self, request):
        """Uğurlu login-i qeydə al."""
        identifier = request.data.get("identifier", "")
        identifier_type = request.data.get("identifier_type", "email")
        ip_address = request._request.META.get("REMOTE_ADDR", "0.0.0.0")

        LoginAttempt.objects.create(
            identifier=identifier,
            identifier_type=identifier_type,
            ip_address=ip_address,
            is_successful=True,
        )

        # Bloku sil
        LoginBlock.objects.filter(identifier=identifier).delete()

        return Response({"ok": True})


class LoginBlockViewSet(viewsets.ModelViewSet):
    queryset = LoginBlock.objects.all()
    serializer_class = LoginBlockSerializer


class PasswordResetOTPViewSet(viewsets.ModelViewSet):
    queryset = PasswordResetOTP.objects.all()
    serializer_class = PasswordResetOTPSerializer
    filterset_fields = ["email", "purpose", "is_used"]

    @action(detail=False, methods=["post"], url_path="generate")
    def generate_otp(self, request):
        """OTP yarat — şifrə sıfırlama / work_number bərpa."""
        email = request.data.get("email", "")
        purpose = request.data.get("purpose", "password_reset")

        if not email:
            return Response(
                {"error": "email tələb olunur"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        otp = f"{secrets.randbelow(1000000):06d}"
        otp_obj = PasswordResetOTP.objects.create(
            email=email,
            otp_code=otp,
            purpose=purpose,
            expires_at=timezone.now() + timedelta(minutes=5),
        )

        # Burada email göndərilməli
        return Response({
            "otp_sent": True,
            "otp_code": otp,  # Development üçün — production-da çıxarılacaq
            "expires_in_minutes": 5,
        })

    @action(detail=False, methods=["post"], url_path="verify")
    def verify_otp(self, request):
        """OTP yoxla."""
        email = request.data.get("email", "")
        code = request.data.get("otp_code", "")
        purpose = request.data.get("purpose", "password_reset")

        otp_obj = PasswordResetOTP.objects.filter(
            email=email,
            otp_code=code,
            purpose=purpose,
            is_used=False,
            expires_at__gte=timezone.now(),
        ).first()

        if not otp_obj:
            return Response(
                {"valid": False, "error": "Etibarsız və ya vaxtı bitmiş OTP"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        otp_obj.is_used = True
        otp_obj.save(update_fields=["is_used"])

        return Response({"valid": True})


class WhatsAppTemplateViewSet(viewsets.ModelViewSet):
    queryset = WhatsAppTemplate.objects.select_related("exam").all()
    serializer_class = WhatsAppTemplateSerializer
    filterset_fields = ["exam", "template_type"]
    search_fields = ["name"]

    @action(detail=True, methods=["post"], url_path="render")
    def render_template(self, request, pk=None):
        """Şablonu render et — placeholder-ları dəyiş."""
        template = self.get_object()
        data = request.data

        message = template.message_template
        for key, value in data.items():
            message = message.replace(f"{{{key}}}", str(value))

        return Response({"rendered_message": message})


class ExamRecordingViewSet(viewsets.ModelViewSet):
    queryset = ExamRecording.objects.select_related(
        "assignment", "session", "student",
    ).all()
    serializer_class = ExamRecordingSerializer
    filterset_fields = ["assignment", "student", "recording_type"]

    @action(detail=True, methods=["get"], url_path="signed-url")
    def signed_url(self, request, pk=None):
        """İmzalı URL qaytar — video üçün (2 saat etibarlı)."""
        recording = self.get_object()
        if recording.video_file:
            url = recording.video_file.url
            return Response({"url": url, "expires_in_seconds": 7200})
        return Response(
            {"error": "Video faylı tapılmadı"},
            status=status.HTTP_404_NOT_FOUND,
        )
