from django.http import HttpResponse
from django.conf import settings
from django.core.mail import EmailMessage

from urllib.request import Request, urlopen
import uuid
import json


def send_mail(subject, message, recipient_list, attach_filename=None, attach_data=None, attach_mime=None):
    email = EmailMessage(
        subject,
        message,
        'noreply@carbase.kz',
        recipient_list
    )
    if attach_data:
        email.attach(attach_filename, attach_data, attach_mime)
    return email.send()


def http_code(message, status):
    ''' Generates HTTP Response '''
    return HttpResponse(message, status=status)


def create_guid():
    ''' creates unique id string '''
    return str(uuid.uuid4().hex)


def re_regestration_fee():
    '''
        calculates fine for automobile using MCI + commission
        formula: "СРТС"<125% of MCI> + "ГРНЗ"<280% of MCI> + "комиссия"<100% of MCI>
    '''
    return (settings.SRTS_TAX * settings.MCI) + (settings.GRNZ_TAX * settings.MCI) + settings.MCI


def post_data(url, data, content_type):
    '''
        posts data as json to specified url
        returns http response data
    '''
    buffer = data.encode('utf-8')
    request = Request(url)
    request.add_header('Content-Type', content_type)
    request.add_header('Content-Length', len(buffer))
    response = urlopen(request, buffer)
    return response.read().decode('utf-8')


def request_to_json(request):
    '''
        converts request body to json
    '''
    data = json.loads(request.body.decode('utf-8'))
    return data


def has_same_chars(chars):
    return chars == len(chars) * chars[0]
