import ast
import operator
import os
import uuid
import calendar
from datetime import date, datetime, timedelta
from email.mime.base import MIMEBase
from functools import reduce
import PyPDF2
from xml.etree import ElementTree
from PyPDF2 import PdfFileReader
from dateutil.parser import parse
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.core.mail import send_mail, EmailMultiAlternatives
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.template.loader import get_template, render_to_string
from django.utils import timezone
from pdf2image import convert_from_path
from rest_framework import generics, status
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework import views, viewsets
from xhtml2pdf import pisa

from apps.core.pagination import LargeResultsSetPagination
from apps.core.queue_system.publisher import BasePublisher
from apps.core.utils import generate_unique_key, render_to_pdf_file, send_email_file_attach
from apps.property.models import Agency, Salutarium, Paper
from apps.property.serializers import AgencySerializer, SalutariumSerializer, PaperSerializer
from apps.users.models import User

class SalutariumViewSet(ModelViewSet):
    queryset = Salutarium.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = SalutariumSerializer
    http_method_names = ['get', 'post', 'patch']

    def get_queryset(self):
        return Salutarium.objects.all()

    def get_object(self):
        queryset = Salutarium.objects.all()
        return get_object_or_404(queryset, user=self.request.user)

    @action(methods=['GET'], detail=False, permission_classes=[], serializer_class=SalutariumSerializer)
    def get(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            serializer = SalutariumSerializer(queryset, many=True)

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
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(user=request.user)
            return JsonResponse({
                'success': True,
                'message': 'Success',
                'result': serializer.data
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            print(e)
            return JsonResponse({
                'success': False,
                'message': 'Error Occured',
                'result': []
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def update(self, request, *args, **kwargs):
        try:
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
        except:
            return JsonResponse({
                'success': False,
                'message': 'Error Occured',
                'result': []
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PaperViewSet(ModelViewSet):
    queryset = Paper.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = PaperSerializer
    http_method_names = ['get', 'post', 'patch']

    def get_queryset(self):
        return Paper.objects.filter(user=self.request.user)

    def get_object(self):
        queryset = Paper.objects.all()
        return get_object_or_404(queryset, user=self.request.user)

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            serializer = PaperSerializer(queryset, many=True)

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
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(methods=['GET'], detail=False, permission_classes=[IsAuthenticated])
    def listByPatient(self, request, *args, **kwargs):
        try:
            queryset = Paper.objects.filter(patient_id=request.GET.get('patient'))
            list = []
            for query in queryset:
                patient = User.objects.get(id=query.patient_id)
                paper = {}
                paper['id'] = query.id
                paper['patient'] = patient.name
                paper['file'] = str(query.file)
                paper['created_at'] = query.created_at
                list.append(paper)
                
            return JsonResponse({
                'success': True,
                'message': 'Success',
                'result': list
            }, status=status.HTTP_200_OK)
        except:
            return JsonResponse({
                'success': False,
                'message': 'Error Occured',
                'result': []
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(methods=['GET'], detail=False, permission_classes=[IsAuthenticated])
    def listByNurse(self, request, *args, **kwargs):
        try:
            queryset = Paper.objects.filter(registerer_id=request.GET.get('registerer'))
            list = []
            for query in queryset:
                patient = User.objects.get(id=query.patient_id)
                paper = {}
                paper['id'] = query.id
                paper['patient'] = patient.name
                paper['file'] = str(query.file)
                paper['created_at'] = query.created_at
                list.append(paper)
                
            return JsonResponse({
                'success': True,
                'message': 'Success',
                'result': list
            }, status=status.HTTP_200_OK)
        except:
            return JsonResponse({
                'success': False,
                'message': 'Error Occured',
                'result': []
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(methods=['GET'], detail=False, permission_classes=[IsAuthenticated])
    def listBySalutarium(self, request, *args, **kwargs):
        try:
            queryset = Paper.objects.filter(salutarium_id=request.GET.get('salutarium'))
            list = []
            for query in queryset:
                patient = User.objects.get(id=query.patient_id)
                paper = {}
                paper['id'] = query.id
                paper['patient'] = patient.name
                paper['file'] = str(query.file)
                paper['created_at'] = query.created_at
                list.append(paper)
                
            return JsonResponse({
                'success': True,
                'message': 'Success',
                'result': list
            }, status=status.HTTP_200_OK)
        except:
            return JsonResponse({
                'success': False,
                'message': 'Error Occured',
                'result': []
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def create(self, request, *args, **kwargs):
        try:
            creation = render_to_pdf_file('mealpaper.htm', request.data)

            if creation['success']:
                patient = User.objects.get(id=request.data['patient'])
                users = User.objects.filter(Q(salutarium=patient.salutarium, role=2) | Q(salutarium=patient.salutarium, role=3))
                to_email = []
                for user in users:
                    to_email.append(user.email)
                
                context = "こんにちは。<br /><br />" + request.user.name + "様が" + patient.name + "様に対する新しい食事箋を送ってきました。<br /><br />確認お願いします。"
                subject = "新しい食事箋が到着しました。"

                send_email_file_attach(
                    to_email,
                    context,
                    subject,
                    [creation['filename']],
                    request.user.email
                )
                paper = Paper(
                    patient = User(id=request.data['patient']),
                    registerer = User(id=request.user.id),
                    salutarium = Salutarium(id=request.user.salutarium_id),
                    file=creation['filename'][13:]
                )
                paper.save()

                return JsonResponse({
                    'success': True,
                    'message': 'Success',
                    'result': {
                        'fileUrl': creation['filename'][13:]
                    }
                }, status=status.HTTP_200_OK)
            else:
                return JsonResponse({
                    'success': False,
                    'message': 'Paper Creation Failed',
                    'result': []
                }, status=status.HTTP_400_BAD_REQUEST)
            return JsonResponse({
                'success': True,
                'message': 'Success',
                'result': []
            })
        except:
            return JsonResponse({
                'success': False,
                'message': 'Error Occured',
                'result': []
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(methods=['POST'], detail=False, permission_classes=[IsAuthenticated])
    def preview(self, request):
        try:
            creation = render_to_pdf_file('mealpaper.htm', request.data)

            if creation['success']:
                return JsonResponse({
                    'success': True,
                    'message': 'Success',
                    'result': {
                        'fileUrl': creation['filename'][13:]
                    }
                }, status=status.HTTP_200_OK)
            else:
                return JsonResponse({
                    'success': False,
                    'message': 'Paper Creation Failed',
                    'result': []
                }, status=status.HTTP_400_BAD_REQUEST)
        except:
            return JsonResponse({
                'success': False,
                'message': 'Error Occured!',
                'result': []
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)