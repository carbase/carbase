from django.http import HttpResponse
from django.conf import settings

from urllib.request import Request, urlopen
import hashlib
import uuid
import json


'''
Generates HTTP Response
'''


def http_code(message, status):
    response = HttpResponse(message, status=status)
    response['Access-Control-Allow-Credentials'] = 'true'
    return response


'''
creates signature based on password string + optional parameters
concatenates in alphabetic order and separated by | symbol
converts string to hash SHA-1
'''


def create_signature(merchant_password, parameters):
    params = str(merchant_password)
    for key, value in sorted(parameters.items()):
        params += '|{}'.format(value)
    buffer = params.encode('utf-8')
    return str(hashlib.sha1(buffer).hexdigest())


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
    return (1.25 * settings.MCI) + (2.80 * settings.MCI) + settings.MCI


'''
posts data as json to specified url
returns http response data
'''


def post_data(url, dictionary):
    data = json.dumps(dictionary)
    buffer = data.encode('utf-8')
    request = Request(url)
    request.add_header('Content-Type', 'application/json; charset=utf-8')
    request.add_header('Content-Length', len(buffer))
    response = urlopen(request, buffer)
    return json.loads(response.read().decode('utf-8'))


'''
converts request body to json
'''


def request_to_json(request):
    data = json.loads(request.body.decode('utf-8'))
    return data

