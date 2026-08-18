from rest_framework import serializers
from ..models import (
    NotificationTemplate, CabinetNotification, CabinetActivity,
    LoginAttempt, LoginBlock, PasswordResetOTP, WhatsAppTemplate,
    ExamRecording,
)


class NotificationTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationTemplate
        fields = "__all__"


class CabinetNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CabinetNotification
        fields = "__all__"


class CabinetActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = CabinetActivity
        fields = "__all__"


class LoginAttemptSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoginAttempt
        fields = "__all__"


class LoginBlockSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoginBlock
        fields = "__all__"


class PasswordResetOTPSerializer(serializers.ModelSerializer):
    class Meta:
        model = PasswordResetOTP
        fields = "__all__"


class WhatsAppTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = WhatsAppTemplate
        fields = "__all__"


class ExamRecordingSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamRecording
        fields = "__all__"
