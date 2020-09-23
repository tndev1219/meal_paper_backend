from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.conf import settings
from rest_framework import status
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.authtoken.models import Token
from rest_framework import generics

from apps.users.filters import UserFilter
from apps.users.models import User
from apps.users.serializers import ResetPasswordSerializer, ForgotPasswordSerializer, SignUpSerializer, UpdateProfileSerializer

class ResetPasswordAPIView(APIView):
    serializer_class = ResetPasswordSerializer

    def get_serializer(self):
        return self.serializer_class()

    def post(self, request, reset_key):
        try:
            context = {
                'request': request,
                'reset_key': reset_key,
            }
            user = User.objects.filter(reset_key=context['reset_key'])
            if user.first() is not None:
                user = user.first()
                serializer = self.serializer_class(
                    data=request.data, context=context)
                serializer.is_valid(raise_exception=True)
                serializer.reset(serializer.data)
                return JsonResponse(
                    {
                        'success': True,
                        'message': 'Success',
                        'result': serializer.data,
                    }, status=status.HTTP_200_OK)
            return JsonResponse({
                'success': False,
                'message': {'detail': 'user not found'},
                'result': []
            }, status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print('Reset password Error: ', e)
            return JsonResponse({
                'success': False,
                'message': 'Error Occured',
                'result': []
            }, status.HTTP_400_BAD_REQUEST)


class ResetEmail(ObtainAuthToken):
    def get_serializer(self):
        return self.serializer_class()

    def post(self, request, *args, **kwargs):
        try:
            serializer = self.serializer_class(
                data=request.data, context={'request': request})
            serializer.is_valid(raise_exception=True)
            user = serializer.validated_data['user']
            user.email = request.data['new_email']
            user.save()

            return JsonResponse({
                'success': True,
                'message': 'Success',
                'result': {
                    'id': user.pk,
                    'email': user.email
                }
            }, status=status.HTTP_200_OK)
        except Exception as e:
            print('Reset Email Error: ', e)
            return JsonResponse({
                'success': False,
                'message': 'Error Occured',
                'result': []
            }, status=status.HTTP_400_BAD_REQUEST)


class ChangePassword(ObtainAuthToken):
    def get_serializer(self):
        return self.serializer_class()

    def post(self, request, *args, **kwargs):
        try:
            serializer = self.serializer_class(
                data=request.data, context={'request': request})
            serializer.is_valid(raise_exception=True)
            user = serializer.validated_data['user']
            user.set_password(request.data['new_password'])
            user.save()

            return JsonResponse({
                'success': True,
                'message': 'Success',
                'result': {
                    'id': user.pk
                }
            }, status=status.HTTP_200_OK)
        except Exception as e:
            print('Change Password Error: ', e)
            return JsonResponse({
                'success': False,
                'message': 'Error Occured',
                'result': []
            }, status=status.HTTP_400_BAD_REQUEST)


class ForgotPasswordAPIView(APIView):
    serializer_class = ForgotPasswordSerializer

    def get_serializer(self):
        return self.serializer_class()

    def post(self, request):
        try:
            serializer = self.serializer_class(data=request.data)
            serializer.is_valid(raise_exception=True)
            reset_key = serializer.send_mail(request.data)
            return JsonResponse(
                {
                    'success': True,
                    'message': 'Success',
                    'result': reset_key,
                }, status=status.HTTP_200_OK)
        except Exception as e:
            print('Forgot Password Error: ', e)
            return JsonResponse(
                {
                    'success': False,
                    'message': serializer.errors,
                    'result': []
                }, status=status.HTTP_400_BAD_REQUEST)


class Login(ObtainAuthToken):
    def get_serializer(self):
        return self.serializer_class()

    def post(self, request, *args, **kwargs):
        try:
            serializer = self.serializer_class(
                data=request.data, context={'request': request})
            serializer.is_valid(raise_exception=True)
            user = serializer.validated_data['user']
            token, created = Token.objects.get_or_create(user=user)

            return JsonResponse({
                'success': True,
                'message': 'Success',
                'result': {
                    'id': user.pk,
                    'email': user.email,
                    'token': token.key,
                    'salutarium': user.salutarium.id,
                    'name': user.name,
                    'role': user.role,
                    'birthday': user.birthday,
                    'gender': user.gender,
                    'age': user.age,
                    'unit_layer': user.unit_layer,
                    'unit_direction': user.unit_direction,
                    'weight': user.weight,
                    'height': user.height,
                    'disease': user.disease,
                    'contact': user.contact,
                    'money': user.money,
                    'emergency_contact': user.emergency_contact,
                    'company': user.company,
                    'address': user.address
                }
            }, status=status.HTTP_200_OK)
        except Exception as e:
            print('Login Error: ', e)
            return JsonResponse({
                'success': False,
                'message': 'Error Occured',
                'result': []
            }, status=status.HTTP_400_BAD_REQUEST)


class SignUpAPIView(APIView):
    serializer_class = SignUpSerializer

    def get_serializer(self):
        return self.serializer_class()

    def post(self, request):
        try:
            serializer = self.serializer_class(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save_user(serializer.data)
            return JsonResponse(
                {
                    'success': True,
                    'message': 'Success',
                    'result': serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )
        except Exception as e:
            print('Sign Up Error: ', e)
            return JsonResponse(
                {
                    'success': False,
                    'message': serializer.errors,
                    'result': [],
                },
                status=status.HTTP_400_BAD_REQUEST,
            )


class UpdateProfileViewSet(ModelViewSet):
    serializer_class = UpdateProfileSerializer
    permission_classes = (IsAuthenticated, )
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_queryset(self):
        salutarium = self.request.GET.get('salutarium')
        role = self.request.GET.get('role')
        return User.objects.filter(salutarium=salutarium, role=role)

    def get_object(self):
        queryset = User.objects.all()
        obj = get_object_or_404(queryset, pk=self.kwargs['pk'])
        return obj

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            serializer = UpdateProfileSerializer(queryset, many=True)
            return JsonResponse({
                'success': True,
                'message': 'Success',
                'result': serializer.data
            }, status=status.HTTP_200_OK)
        except:
            return JsonResponse({
                'success': False,
                'message': 'Error Occured',
                'result': []
            }, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        try:
            user = User.objects.filter(id=kwargs['pk'])
            if user:
                partial = kwargs.pop('partial', True)
                instance = self.get_object()
                serializer = self.get_serializer(
                    instance, data=request.data, partial=partial)
                serializer.is_valid(raise_exception=True)
                self.perform_update(serializer)

                return JsonResponse({
                    'success': True,
                    'message': 'Success',
                    'result': serializer.data
                }, status=status.HTTP_200_OK)
            else:
                return JsonResponse({
                    'success': False,
                    'message': 'User Not Found',
                    'result': []
                }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            print('Update Profile Error: ', e)
            return JsonResponse({
                'success': False,
                'message': 'Error Occured',
                'result': []
            }, status=status.HTTP_400_BAD_REQUEST)
