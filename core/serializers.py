from rest_framework import serializers

from core.models import Contact


class ContactSerializer(serializers.ModelSerializer):

    class Meta:
        model = Contact
        fields = ['id', 'first_name', 'last_name', 'email', 'phone', 'message', 'created_at']
        read_only_fields = ['id', 'created_at']
