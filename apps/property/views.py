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
from apps.core.utils import generate_unique_key, render_to_pdf_file, send_email_file_attach, get_era, get_era_year
from apps.property.models import Agency, Salutarium, Paper, DeviceToken
from apps.property.serializers import AgencySerializer, SalutariumSerializer, PaperSerializer, DeviceTokenSerializer
from apps.users.models import User

class AgencyViewSet(ModelViewSet):
    queryset = Agency.objects.all()
    permission_classes = (IsAuthenticated, )
    serializer_class = AgencySerializer
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_queryset(self):
        return Agency.objects.all()

    def get_object(self):
        queryset = Agency.objects.all()
        return get_object_or_404(queryset, pk=self.kwargs['pk'])

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            serializer = AgencySerializer(queryset, many=True)

            return JsonResponse({
                'success': True,
                'message': 'Success',
                'result': serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return JsonResponse({
                'success': False,
                'message': 'Error Occured',
                'result': []
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            user = User(
                role = 5,
                email = request.data['email'],
                username = request.data['email'],
                password = "password"
            )
            user.save()
            serializer.save()
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
        except Exception as e:
            print(e)
            return JsonResponse({
                'success': False,
                'message': 'Error Occured',
                'result': []
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def destroy(self, request, *args, **kwargs):
        try:
            instance = Agency.objects.get(id=kwargs['pk'])
            self.perform_destroy(instance)
            return JsonResponse({
                'success': True,
                'message': 'Success',
                'result': []
            }, status=status.HTTP_200_OK)
        except:
            return JsonResponse({
                'success': False,
                'message': 'Error Occured!',
                'result': []
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(methods=['POST'], detail=False, permission_classes=[IsAuthenticated])
    def multiDel(self, request, *args, **kwargs):
        try:
            for id in request.data['ids']:
                instance = Agency.objects.get(id=id)
                self.perform_destroy(instance)
            return JsonResponse({
                'success': True,
                'message': 'Success',
                'result': []
            }, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return JsonResponse({
                'success': False,
                'message': 'Error Occured!',
                'result': []
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SalutariumViewSet(ModelViewSet):
    queryset = Salutarium.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = SalutariumSerializer
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_queryset(self):
        return Salutarium.objects.all()

    def get_object(self):
        queryset = Salutarium.objects.all()
        return get_object_or_404(queryset, pk=self.kwargs['pk'])

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

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            serializer = SalutariumSerializer(queryset, many=True)

            result = []
            for data in serializer.data:
                agency = Agency.objects.get(id=data['agency'])
                temp = {
                    'id': data['id'],
                    'agency': agency.id,
                    'agency_name': agency.name,
                    'name': data['name'],
                    'treasurer_name': data['treasurer_name'],
                    'contact': data['contact'],
                    'created_at': data['created_at']
                }
                result.append(temp)

            return JsonResponse({
                'success': True,
                'message': 'Success',
                'result': result
            }, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
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

    def destroy(self, request, *args, **kwargs):
        try:
            instance = Salutarium.objects.get(id=kwargs['pk'])
            self.perform_destroy(instance)
            return JsonResponse({
                'success': True,
                'message': 'Success',
                'result': []
            }, status=status.HTTP_200_OK)
        except:
            return JsonResponse({
                'success': False,
                'message': 'Error Occured!',
                'result': []
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(methods=['POST'], detail=False, permission_classes=[IsAuthenticated])
    def multiDel(self, request, *args, **kwargs):
        try:
            for id in request.data['ids']:
                instance = Salutarium.objects.get(id=id)
                self.perform_destroy(instance)
            return JsonResponse({
                'success': True,
                'message': 'Success',
                'result': []
            }, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return JsonResponse({
                'success': False,
                'message': 'Error Occured!',
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
            patient = User.objects.get(id=request.data['patient'])
            registerer = User.objects.get(id=request.user.id)

            today = date.today()
            d1 = today.strftime("%Y-%m-%d")

            context = {}
            context['registerer_name'] = registerer.name
            context['register_era'] = get_era(int(str(d1).split('-')[0]))
            context['register_era_year'] = get_era_year(int(str(d1).split('-')[0]))
            context['register_month'] = str(d1).split('-')[1]
            context['register_day'] = str(d1).split('-')[2]

            context['patient_name'] = patient.name
            context['patient_era'] = get_era(int(str(patient.birthday).split('-')[0]))
            context['patient_era_year'] = get_era_year(int(str(patient.birthday).split('-')[0]))
            context['patient_year'] = str(patient.birthday).split('-')[0]
            context['patient_month'] = str(patient.birthday).split('-')[1]
            context['patient_day'] = str(patient.birthday).split('-')[2]
            if patient.gender:
                context['patient_gender'] = '男'
            else:
                context['patient_gender'] = '女'
            context['patient_age'] = patient.age
            context['patient_unit_layer'] = patient.unit_layer
            if patient.unit_direction:
                context['patient_unit_direction'] = '北'
            else:
                context['patient_unit_direction'] = '南'
            context['patient_height'] = patient.height
            context['patient_weight'] = patient.weight
            context['patient_disease'] = patient.disease

            if request.data['period']:
                context['period'] = '入所'
            else:
                context['period'] = 'ショート'

            if request.data['reason'] == 1:
                context['reason'] = '入所'
            elif request.data['reason'] == 2:
                context['reason'] = '変更'
            elif request.data['reason'] == 3:
                context['reason'] = '入院'
            elif request.data['reason'] == 4:
                context['reason'] = '外出'
            elif request.data['reason'] == 5:
                context['reason'] = '外泊'
            elif request.data['reason'] == 6:
                context['reason'] = '退所'
            elif request.data['reason'] == 7:
                context['reason'] = '中止'

            context['start_date_era'] = get_era(int(request.data['start_date'].split('-')[0]))
            context['start_date_era_year'] = get_era_year(int(request.data['start_date'].split('-')[0]))
            context['start_date_month'] = request.data['start_date'].split('-')[1]
            context['start_date_day'] = request.data['start_date'].split('-')[2]

            context['end_date_era'] = get_era(int(request.data['end_date'].split('-')[0]))
            context['end_date_era_year'] = get_era_year(int(request.data['end_date'].split('-')[0]))
            context['end_date_month'] = request.data['end_date'].split('-')[1]
            context['end_date_day'] = request.data['end_date'].split('-')[2]

            if request.data['time']:
                if request.data['time_start'] == 1:
                    context['time_start'] = '朝'
                elif request.data['time_start'] == 2:
                    context['time_start'] = '昼'
                elif request.data['time_start'] == 3:
                    context['time_start'] = 'おやつ'
                elif request.data['time_start'] == 4:
                    context['time_start'] = '夕'

                if request.data['time_end'] == 1:
                    context['time_end'] = '朝'
                elif request.data['time_end'] == 2:
                    context['time_end'] = '昼'
                elif request.data['time_end'] == 3:
                    context['time_end'] = 'おやつ'
                elif request.data['time_end'] == 4:
                    context['time_end'] = '夕'

                context['time_start_suffix'] = 'から'
                context['time_end_suffix'] = 'まで'
            else:
                if request.data['time_start'] == 1:
                    context['time_start'] = '朝'
                    context['time_end'] = '朝'
                elif request.data['time_start'] == 2:
                    context['time_start'] = '昼'
                    context['time_end'] = '昼'
                elif request.data['time_start'] == 3:
                    context['time_start'] = 'おやつ'
                    context['time_end'] = 'おやつ'
                elif request.data['time_start'] == 4:
                    context['time_start'] = '夕'
                    context['time_end'] = '夕'

                context['time_start_suffix'] = 'のみ'
                context['time_end_suffix'] = 'のみ'

            if request.data['meal_various'] == 1:
                context['meal_various'] = '普通食'
            elif request.data['meal_various'] == 2:
                context['meal_various'] = 'ミキサー食'
            elif request.data['meal_various'] == 3:
                context['meal_various'] = '腹部エコー検査食'
            elif request.data['meal_various'] == 4:
                context['meal_various'] = '糖尿食1'
            elif request.data['meal_various'] == 5:
                context['meal_various'] = '糖尿食2'
            elif request.data['meal_various'] == 6:
                context['meal_various'] = '减塩食1'
            elif request.data['meal_various'] == 7:
                context['meal_various'] = '减塩食2'
            elif request.data['meal_various'] == 8:
                context['meal_various'] = '腎臓食1'
            elif request.data['meal_various'] == 9:
                context['meal_various'] = '腎臓食2'

            if request.data['main_meal'] == 1:
                context['main_meal'] = '米飯'
            elif request.data['main_meal'] == 2:
                context['main_meal'] = '軟飯'
            elif request.data['main_meal'] == 3:
                context['main_meal'] = '全粥'
            elif request.data['main_meal'] == 4:
                context['main_meal'] = 'ミキサー粥'
            elif request.data['main_meal'] == 5:
                context['main_meal'] = 'おにぎり  ' + request.data['meal_count'] + '個'

            if request.data['form'] == 1:
                context['form'] = '普通'
            elif request.data['form'] == 2:
                context['form'] = '一口大'
            elif request.data['form'] == 3:
                context['form'] = '刻み'
            elif request.data['form'] == 4:
                context['form'] = '極刻み'
            elif request.data['form'] == 5:
                context['form'] = 'ミキサー'

            context['baned_meal'] = request.data['baned_meal']
            context['other'] = request.data['other']

            creation = render_to_pdf_file('mealpaper.html', context)

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
        except Exception as e:
            print(e)
            return JsonResponse({
                'success': False,
                'message': 'Error Occured',
                'result': []
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(methods=['POST'], detail=False, permission_classes=[IsAuthenticated])
    def preview(self, request):
        try:
            patient = User.objects.get(id=request.data['patient'])
            registerer = User.objects.get(id=request.user.id)

            today = date.today()
            d1 = today.strftime("%Y-%m-%d")

            context = {}
            context['registerer_name'] = registerer.name
            context['register_era'] = get_era(int(str(d1).split('-')[0]))
            context['register_era_year'] = get_era_year(int(str(d1).split('-')[0]))
            context['register_month'] = str(d1).split('-')[1]
            context['register_day'] = str(d1).split('-')[2]

            context['patient_name'] = patient.name
            context['patient_era'] = get_era(int(str(patient.birthday).split('-')[0]))
            context['patient_era_year'] = get_era_year(int(str(patient.birthday).split('-')[0]))
            context['patient_year'] = str(patient.birthday).split('-')[0]
            context['patient_month'] = str(patient.birthday).split('-')[1]
            context['patient_day'] = str(patient.birthday).split('-')[2]
            if patient.gender:
                context['patient_gender'] = '男'
            else:
                context['patient_gender'] = '女'
            context['patient_age'] = patient.age
            context['patient_unit_layer'] = patient.unit_layer
            if patient.unit_direction:
                context['patient_unit_direction'] = '北'
            else:
                context['patient_unit_direction'] = '南'
            context['patient_height'] = patient.height
            context['patient_weight'] = patient.weight
            context['patient_disease'] = patient.disease

            if request.data['period']:
                context['period'] = '入所'
            else:
                context['period'] = 'ショート'

            if request.data['reason'] == 1:
                context['reason'] = '入所'
            elif request.data['reason'] == 2:
                context['reason'] = '変更'
            elif request.data['reason'] == 3:
                context['reason'] = '入院'
            elif request.data['reason'] == 4:
                context['reason'] = '外出'
            elif request.data['reason'] == 5:
                context['reason'] = '外泊'
            elif request.data['reason'] == 6:
                context['reason'] = '退所'
            elif request.data['reason'] == 7:
                context['reason'] = '中止'

            context['start_date_era'] = get_era(int(request.data['start_date'].split('-')[0]))
            context['start_date_era_year'] = get_era_year(int(request.data['start_date'].split('-')[0]))
            context['start_date_month'] = request.data['start_date'].split('-')[1]
            context['start_date_day'] = request.data['start_date'].split('-')[2]

            context['end_date_era'] = get_era(int(request.data['end_date'].split('-')[0]))
            context['end_date_era_year'] = get_era_year(int(request.data['end_date'].split('-')[0]))
            context['end_date_month'] = request.data['end_date'].split('-')[1]
            context['end_date_day'] = request.data['end_date'].split('-')[2]

            if request.data['time']:
                if request.data['time_start'] == 1:
                    context['time_start'] = '朝'
                elif request.data['time_start'] == 2:
                    context['time_start'] = '昼'
                elif request.data['time_start'] == 3:
                    context['time_start'] = 'おやつ'
                elif request.data['time_start'] == 4:
                    context['time_start'] = '夕'

                if request.data['time_end'] == 1:
                    context['time_end'] = '朝'
                elif request.data['time_end'] == 2:
                    context['time_end'] = '昼'
                elif request.data['time_end'] == 3:
                    context['time_end'] = 'おやつ'
                elif request.data['time_end'] == 4:
                    context['time_end'] = '夕'

                context['time_start_suffix'] = 'から'
                context['time_end_suffix'] = 'まで'
            else:
                if request.data['time_start'] == 1:
                    context['time_start'] = '朝'
                    context['time_end'] = '朝'
                elif request.data['time_start'] == 2:
                    context['time_start'] = '昼'
                    context['time_end'] = '昼'
                elif request.data['time_start'] == 3:
                    context['time_start'] = 'おやつ'
                    context['time_end'] = 'おやつ'
                elif request.data['time_start'] == 4:
                    context['time_start'] = '夕'
                    context['time_end'] = '夕'

                context['time_start_suffix'] = 'のみ'
                context['time_end_suffix'] = 'のみ'

            if request.data['meal_various'] == 1:
                context['meal_various'] = '普通食'
            elif request.data['meal_various'] == 2:
                context['meal_various'] = 'ミキサー食'
            elif request.data['meal_various'] == 3:
                context['meal_various'] = '腹部エコー検査食'
            elif request.data['meal_various'] == 4:
                context['meal_various'] = '糖尿食1'
            elif request.data['meal_various'] == 5:
                context['meal_various'] = '糖尿食2'
            elif request.data['meal_various'] == 6:
                context['meal_various'] = '减塩食1'
            elif request.data['meal_various'] == 7:
                context['meal_various'] = '减塩食2'
            elif request.data['meal_various'] == 8:
                context['meal_various'] = '腎臓食1'
            elif request.data['meal_various'] == 9:
                context['meal_various'] = '腎臓食2'

            if request.data['main_meal'] == 1:
                context['main_meal'] = '米飯'
            elif request.data['main_meal'] == 2:
                context['main_meal'] = '軟飯'
            elif request.data['main_meal'] == 3:
                context['main_meal'] = '全粥'
            elif request.data['main_meal'] == 4:
                context['main_meal'] = 'ミキサー粥'
            elif request.data['main_meal'] == 5:
                context['main_meal'] = 'おにぎり  ' + request.data['meal_count'] + '個'

            if request.data['form'] == 1:
                context['form'] = '普通'
            elif request.data['form'] == 2:
                context['form'] = '一口大'
            elif request.data['form'] == 3:
                context['form'] = '刻み'
            elif request.data['form'] == 4:
                context['form'] = '極刻み'
            elif request.data['form'] == 5:
                context['form'] = 'ミキサー'

            context['baned_meal'] = request.data['baned_meal']
            context['other'] = request.data['other']

            context['salutarium'] = patient.salutarium.name

            creation = render_to_pdf_file('mealpaper.html', context)

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
        except Exception as e:
            print(e)
            return JsonResponse({
                'success': False,
                'message': 'Error Occured!',
                'result': []
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DeviceTokenViewSet(ModelViewSet):
    queryset = DeviceToken.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = DeviceTokenSerializer
    http_method_names = ['get', 'post', 'patch']

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            instance = DeviceToken.objects.filter(user=request.user)
            if len(instance) == 0:
                serializer.save(user=request.user)
            else:
                salutarium = Salutarium.objects.get(id=request.data['salutarium'])
                deviceToken = instance[0]
                deviceToken.token = request.data['token']
                deviceToken.save()
                
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
