import logging
import requests
import json

from django.contrib.postgres.fields import ArrayField
from django.contrib.postgres.fields import JSONField
from django.db import models

from django.db.models import Q
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from apps.core.models import AbstractBaseModel
from apps.users.models import User
# from pmt_api.settings.base import API_BASE_URL

log = logging.getLogger(__name__)

_property = property

class Agency(AbstractBaseModel):
    code = models.CharField(blank=True, null=True, max_length=20)
    name = models.CharField(blank=True, null=True, max_length=100)
    treasurer_name = models.CharField(blank=True, null=True, max_length=100)
    contact = models.CharField(blank=True, null=True, max_length=20)

    def __unicode__(self):
        return self.pk
    
    def to_dict(self):
        result = {}
        result['id'] = self.id
        result['code'] = self.code
        result['name'] = self.name
        result['treasurer_name'] = self.treasurer_name
        result['contact'] = self.contact
        return result

    class Meta:
        verbose_name_plural = 'Agency'

class Salutarium(AbstractBaseModel):
    agency = models.ForeignKey(Agency, on_delete=models.CASCADE, blank=True, null=True)
    name = models.CharField(blank=True, null=True, max_length=100)
    treasurer_name = models.CharField(blank=True, null=True, max_length=100)
    contact = models.CharField(blank=True, null=True, max_length=20)

    def __unicode__(self):
        return self.pk

    def to_dict(self):
        result = {}
        result['id'] = self.id
        result['agency'] = self.agency
        result['name'] = self.name
        result['treasurer_name'] = self.treasurer_name
        result['contact'] = self.contact
        return result

    class Meta:
        verbose_name_plural = 'Salutarium'

class Paper(AbstractBaseModel):
    registerer = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name='registerer')
    patient = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name='patient')
    salutarium = models.ForeignKey(Salutarium, on_delete=models.CASCADE, blank=True, null=True)
    file = models.FileField(blank=True, null=True, upload_to='documents')

    def __unicode__(self):
        return self.pk

    def to_dict(self):
        result = {}
        result['id'] = self.id
        result['registerer'] = self.registerer
        result['patient'] = self.patient
        result['file'] = self.file
        return result

    class Meta:
        verbose_name_plural = 'Paper'

class DeviceToken(AbstractBaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    salutarium = models.ForeignKey(Salutarium, on_delete=models.CASCADE, blank=True, null=True)
    role = models.IntegerField(blank=True, null=True)
    token = models.CharField(blank=True, null=True, max_length=255)

    def __unicode__(self):
        return self.pk

    def to_dict(self):
        result = {}
        result['id'] = self.id
        result['id'] = self.id
        result['salutarium'] = self.salutarium
        result['role'] = self.role
        result['token'] = self.token
    
    class Meta:
        verbose_name_plural = 'DeviceToken'

@receiver(post_save, sender=Paper, dispatch_uid="send_notification")
def send_notification(sender, instance, created, **kwargs):
    if created:
        user = User.objects.get(id=instance.registerer_id)
        deviceTokens = DeviceToken.objects.filter(Q(salutarium=user.salutarium, role=2) | Q(salutarium=user.salutarium, role=3))

        tokens = []
        for item in deviceTokens:
            tokens.append(item.token)
        
        if len(tokens) != 0:
            headers = {
                "Content-Type": "application/json",
                "Authorization": "key=AAAAzeYmouk:APA91bHEmtQSYKd-9iOl1Q-a4V_yR89GPtRDOK2qyzWrUmJ5vei40-BmU6JCzfWxqety-LVZyDxrqR_GphEILJ_MO3Op1CHW4Tz5IkqAuFkMyZAOnKkeL-kDRjOnndAFtqS_QuZf-ctL"
            }
            notification = {
                # "title": "wow",
                "body": "新しい食事箋が登録されました。",
                "content_available": "true"
            }

            body = {
                "registration_ids": tokens,
                "notification": notification
            }

            url = "https://fcm.googleapis.com/fcm/send"
            res = requests.post(url=url, data=json.dumps(body), headers=headers)
            print('Notification Result:', res)