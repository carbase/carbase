from urllib.request import HTTPError, URLError
from urllib.parse import urlparse, urlsplit

import json
import hashlib
import xml.etree.cElementTree as ET

from cars.api import pay_by_id
from django.conf import settings

from carbase.helpers import create_guid, post_data, request_to_json


def sign(script, secret_key, parameters):
    params = str(script)
    for key, value in sorted(parameters.items()):
        params += ';{}'.format(value)
    params += ';' + secret_key
    buffer = params.encode('utf-8')
    return str(hashlib.md5(buffer).hexdigest())


def get_exception(code, reason):
    return {
        'response': {
            'pg_status':            'error',
            'pg_error_code':        str(code),
            'pg_error_description': str(reason),
        }
    }


def do_request(url, params):
    try:
        content_type = 'application/json; charset=utf-8'
        data = post_data(url, json.dumps(params), content_type)
        root = ET.fromstring(data)
        return {'response': {x.tag: root.find(x.tag).text for x in root}}
    except HTTPError as ex:
        return get_exception(ex.code, ex.reason)
    except URLError as ex:
        return get_exception(400, ex.reason)


def get_checkout_url(parameters):

    amount          = parameters.get('amount', 0)
    description     = parameters.get('order_desc', '')
    order_id        = '{}:{}'.format(parameters.get('product_id', ''), create_guid())
    merchant_id     = settings.PAYBOX['MERCHANT_ID']
    secret_key      = settings.PAYBOX['SECRET_KEY']
    script_url      = settings.PAYBOX['SCRIPT_URL']
    result_url      = settings.PAYBOX['RESULT_URL']
    testing_mode    = settings.PAYBOX['TESTING_MODE']
    script          = urlparse(script_url).path[1:]
    salt            = settings.SECRET_KEY

    params = {
        'pg_merchant_id':       merchant_id,
        'pg_amount':            amount,
        'pg_description':       description,
        'pg_order_id':          order_id,
        'pg_salt':              salt,
        'pg_result_url':        result_url,
        'pg_testing_mode':      testing_mode,
    }
    params['pg_sig'] = sign(script, secret_key, params)

    data = do_request(script_url, params)
    data['response']['order_id'] = order_id

    return data


'''
def get_order_status(order_id):

    merchant_id = settings.FONDY']['MERCHANT_ID']
    transaction_password = settings.FONDY']['TRANSACTION_PASSWORD']

    params = {
        'order_id':     order_id,
        'merchant_id':  merchant_id,
    }
    params['signature'] = create_signature(transaction_password, params)

    url = settings.FONDY']['STATUS_URL']
    data = do_request(url, params)

    return data


def set_callback(request):

    data = request_to_json(request)
    status = data['order_status']
    product_id = data['product_id']

    if status == 'approved':
        pay_by_id(product_id)
    else:
        return 1

    return 0
'''
