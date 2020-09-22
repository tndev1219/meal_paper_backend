import os
import base64
import datetime
import hashlib
import json
import random
import string
import uuid
from io import BytesIO

from django.conf import settings
from django.core import serializers
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.template.loader import get_template
from rest_framework.response import Response
from xhtml2pdf import pisa
from datetime import datetime

from apps.core.queue_system.publisher import BasePublisher


def generate_unique_key(value, length=26):
    """
    generate key from passed value
    :param value:
    :param length: key length
    :return:
    """

    salt = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(26)).encode(
        'utf-8')
    value = value.encode('utf-8')
    unique_key = hashlib.sha1(salt + value).hexdigest()

    return unique_key[:length]


def send_email_job(to, template, context, subject):
    from_email = settings.SENDER_EMAIL
    to_email = [to]

    context['client_side_url'] = settings.CLIENT_BASE_URL

    # New job
    BasePublisher(
        routing_key='core.send_email',
        body={
            'context': context,
            'to': to_email,
            'from_email': from_email,
            'template': template,
            'subject': subject,
        }
    )


def send_email_file_attach(email, context, subject, files, from_email):
    html = get_template('email/invoice_email.html')
    body = {'context': context}
    html_content = html.render(body)
    msg = EmailMultiAlternatives(subject, html_content, from_email, email)
    if files:
        for attached_file in files:
            # file_name = os.path.basename(attached_file)
            # data = open(attached_file, 'rb').read()
            # encoded = base64.b64encode(data)
            # msg.attach(file_name, encoded, mimetype='application/octet-stream')
            msg.attach_file(attached_file)
    msg.content_subtype = 'html'
    msg.send()


def model_to_dict(instance):
    """
    Generate dict object from received model instance
    :param instance:
    :return: dict
    """

    serialized_instance = json.loads(serializers.serialize('json', [instance, ]))[0]
    instance_dict = serialized_instance['fields']

    # add instance pk to the fields dict
    instance_dict['id'] = serialized_instance['pk']

    return instance_dict


def get_file_path(filename, folder):
    """
    generate file path for field
    :param filename: selected file name
    :param folder: upload destination folder
    :return:
    """

    if hasattr(settings, 'AMAZON_S3_BUCKET'):
        folder = settings.AMAZON_S3_BUCKET + '/' + folder

    ext = filename.split('.')[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)

    return folder + '/' + filename


def add_list_to_request(request, key):
    """
    # Fix list field issue when content-type is not www-urlencoded
    :param request:
    :param key:
    :return:
    """

    if key in request.data:
        try:
            data = json.loads(request.data[key])
        except (TypeError, ValueError,):
            return

        request.data.setlist(key, data)


def increase_month(date, month):
    """
    Increase Month
    :param date:
    :param month:
    :return:
    """

    m, y = (date.month + month) % 12, date.year + (date.month + month - 1) // 12
    if not m:
        m = 12
    d = min(date.day,
            [31, 29 if y % 4 == 0 and not y % 400 == 0 else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][m - 1])

    return date.replace(day=d, month=m, year=y)


def generate_html_list(objects_list):
    """
    Generates HTML <ul> <li> </li> </ul> lists from received objects_list
    :param objects_list: list of strings
    :return: (string) Html list
    """

    result = '<ul>'
    for object in objects_list:
        result += '<li> {0} </li>'.format(object)
    result += '</ul>'

    return result


def return_http_error(error, status_code):
    return Response(status=status_code, data={
        "code": status_code,
        "detail": "Please enter a valid data",
        "developer_message": "Please enter a valid data",
        "errors": error,
        "status": status_code,
        "timestamp": datetime.datetime.now(),
        "title": "Error"
    })


def render_to_pdf_file(template_src, context_dict={}):
    path_pdf = 'collectstatic/pdfs'
    template = get_template(template_src)
    html = template.render(context_dict)
    result = BytesIO()
    filename = datetime.now().strftime('%Y%m%d%H%M%S') + '.pdf'
    filepath = os.path.join(path_pdf, filename)
    resultFile = open(filepath, "w+b")
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), resultFile)
    resultFile.close()
    return {
        "success": ~pdf.err,
        "filename": filepath
    }