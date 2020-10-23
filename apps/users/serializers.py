from rest_framework import serializers

from apps.core.utils import generate_unique_key
from apps.users.models import User
from apps.property.models import Salutarium
from apps.users.validators import check_valid_password
import requests

from django.core.mail import send_mail, EmailMultiAlternatives
from django.conf import settings

class ResetPasswordSerializer(serializers.Serializer):
    password = serializers.CharField()
    repeat_password = serializers.CharField()

    def reset(self, validated_data):
        user = User.objects.get(reset_key=self.context['reset_key'])
        user.set_password(validated_data['password'])
        user.reset_key = None
        user.save()

    # def validate(self, data):
    #     error = check_valid_password(data)
    #     if error:
    #         raise serializers.ValidationError({'detail': 'password not match or This password is too short'})
    #     return data

    def check_valid_token(self):
        if not User.objects.filter(reset_key=self.context['reset_key']).exists():
            raise serializers.ValidationError({'detail': 'Token is not valid.'})


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

    @staticmethod
    def send_mail(validated_data):
        user = User.objects.get(email=validated_data['email'])
        user.reset_key = generate_unique_key(user.email)

        subject, from_email, to = 'パスワードを忘れたのですか。', settings.SENDER_EMAIL, validated_data['email']
        text_content = '下記の認証コードを利用してパスワードを再設定できます。'
        html_content = ' \
            <br> \
                '+user.name+'様 こんにちは。\
            <br> \
                私たちのサービスを利用していただき、ありがとうございます。\
            <br> \
                あなたは最近、あなたの"食事箋"アカウントのためのパスワードを再設定するための要請を送りました。 \
            <br> \
                下記の認証コードを利用してパスワードを再設定できます。\
            <br> \
            <p>パスワードを再設定するには、 \
                <b> \
                    <strong>'+user.reset_key+'</strong> \
                </b> \
                を入力してください。 このメールを送ったことがないなら無視してもいいです。\
            </p>'
        msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
        msg.attach_alternative(html_content, "text/html")
        msg.send()

        user.save()
        
        return user.reset_key

    def validate(self, data):
        self.check_email(data['email'])
        return data

    @staticmethod
    def check_email(value):
        user = User.objects.filter(email=value)

        if not user.exists():
            raise serializers.ValidationError({'detail': 'This email address does not exist.'})

        if not user.filter(is_active=True).exists():
            raise serializers.ValidationError({'detail': 'Your account is inactive.'})

        return value


class SignUpSerializer(serializers.Serializer):
    role = serializers.IntegerField(required=True, allow_null=False)
    email = serializers.EmailField(required=True, allow_null=False)
    password = serializers.CharField(required=True, allow_null=False)
    salutarium = serializers.PrimaryKeyRelatedField(
        queryset=Salutarium.objects.all(),
        required=False,
        allow_null=True
    )
    name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    birthday = serializers.DateField(required=False, allow_null=True)
    gender = serializers.NullBooleanField(required=False)
    age = serializers.IntegerField(required=False, allow_null=True)
    unit_layer = serializers.CharField(required=False, allow_null=True)
    weight = serializers.FloatField(required=False, allow_null=True)
    height = serializers.FloatField(required=False, allow_null=True)
    disease = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    contact = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    money = serializers.FloatField(required=False, allow_null=True)
    emergency_contact = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    company = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    address = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'username'
        ]
    
    @staticmethod
    def save_user(validated_data):
        user = User(email=validated_data['email'])
        user.set_password(validated_data['password'])
        user.username = validated_data['email']
        if validated_data['salutarium']:
            salutarium = Salutarium(id=validated_data['salutarium'])
            user.salutarium = salutarium
        user.role = validated_data['role']
        user.name = validated_data['name']
        user.birthday = validated_data['birthday']
        user.gender = validated_data['gender']
        user.age = validated_data['age']
        user.unit_layer = validated_data['unit_layer']
        user.weight = validated_data['weight']
        user.height = validated_data['height']
        user.disease = validated_data['disease']
        user.contact = validated_data['contact']
        user.money = validated_data['money']
        user.emergency_contact = validated_data['emergency_contact']
        user.company = validated_data['company']
        user.address = validated_data['address']

        user.save()

    def validate(self, data):
        if User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError({'detail': 'This email address already exists.'})
        return data


class UpdateProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = '__all__'
