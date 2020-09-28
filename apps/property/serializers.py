from django.contrib.postgres.fields import ArrayField
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from rest_framework import serializers

from apps.property.models import Agency, Salutarium, Paper, DeviceToken
from apps.users.models import User
from mealpaper.settings.base import SENDER_EMAIL


class AgencySerializer(serializers.ModelSerializer):
    code = serializers.CharField(required=True, allow_null=False)
    name = serializers.CharField(required=True, allow_null=False)
    treasurer_name = serializers.CharField(required=True, allow_null=False)
    contact = serializers.CharField(required=True, allow_null=False)
    
    class Meta:
        model = Agency
        fields = '__all__'

class SalutariumSerializer(serializers.ModelSerializer):
    agency = serializers.PrimaryKeyRelatedField(
        queryset=Agency.objects.all(),
        required=True,
        allow_null=False
    )
    name = serializers.CharField(required=True, allow_null=False)
    treasurer_name = serializers.CharField(required=True, allow_null=False)
    contact = serializers.CharField(required=True, allow_null=False)

    class Meta:
        model = Salutarium
        fields = [
            'id',
            'agency',
            'name',
            'treasurer_name',
            'contact',
            'created_at'
        ]

class PaperSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Paper
        fields = '__all__'

class DeviceTokenSerializer(serializers.ModelSerializer):
    salutarium = serializers.PrimaryKeyRelatedField(
        queryset=Salutarium.objects.all(),
        required=True,
        allow_null=False
    )
    role = serializers.IntegerField(required=True, allow_null=False)
    token = serializers.CharField(required=True, allow_null=False)

    class Meta:
        model = DeviceToken
        fields = [
            'id',
            'user',
            'salutarium',
            'role',
            'token'
        ]
