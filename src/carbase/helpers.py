from django.http import HttpResponse
from django.conf import settings

from urllib.request import Request, urlopen
import uuid
import json


'''
Generates HTTP Response
'''


def http_code(message, status):
    return HttpResponse(message, status=status)


'''
creates unique id string
'''


def create_guid():
    return str(uuid.uuid4().hex)


'''
calculates fine for automobile using MCI + commission
formula: "СРТС"<125% of MCI> + "ГРНЗ"<280% of MCI> + "комиссия"<100% of MCI>
'''


def re_regestration_fee():
    return (settings.SRTS_TAX * settings.MCI) + (settings.GRNZ_TAX * settings.MCI) + settings.MCI


'''
posts data as json to specified url
returns http response data
'''


def post_data(url, data, content_type):
    buffer = data.encode('utf-8')
    request = Request(url)
    request.add_header('Content-Type', content_type)
    request.add_header('Content-Length', len(buffer))
    response = urlopen(request, buffer)
    return response.read().decode('utf-8')


'''
converts request body to json
'''


def request_to_json(request):
    data = json.loads(request.body.decode('utf-8'))
    return data