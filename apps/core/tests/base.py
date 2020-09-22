# -*- coding: utf-8 -*-

import logging

from django.core.urlresolvers import reverse
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from apps.users.models import User

logging.disable(logging.INFO)


class BaseTestCase(APITestCase):
    """
    Base test case to provide more organized behavior.
    Extend all test cases from this one.
    """

    lookup_field = None
    model = None

    admin_user = {
        'email': 'admin@car.codebnb.me',
        'password': 'car'
    }

    def setUp(self):
        self.__set_auth_token()

    def _generate_url(self, name, pk=None):
        """
        Generate URL by reverse() method
        :param name:
        :param pk:
        :return: url
        """
        if pk is None:
            return reverse('api:{0}-list'.format(name))

        return reverse('api:{0}-detail'.format(name), args=[pk])

    def _get_pk_value(self):

        if self.lookup_field:
            pk = getattr(self.model.objects.first(), self.lookup_field)
        else:
            pk = self.model.objects.first().pk

        return pk

    def __set_auth_token(self):

        token = self.__get_user_token()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token)

    def __get_user_token(self):

        if User.objects.all().exists():
            user = User.objects.first()
        else:
            user = User.objects.create_superuser(**self.admin_user)

        token, created = Token.objects.get_or_create(user=user)
        return token.key
