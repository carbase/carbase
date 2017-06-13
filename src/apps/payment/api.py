from urllib.request import HTTPError, URLError
from urllib.parse import urlparse, urlsplit, parse_qsl

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

    amount = parameters.get('amount', 0)
    description = parameters.get('order_desc', '')
    order_id = '{}:{}'.format(parameters.get('product_id', ''), create_guid())
    merchant_id = settings.PAYBOX['MERCHANT_ID']
    secret_key = settings.PAYBOX['SECRET_KEY']
    payment_url = settings.PAYBOX['PAYMENT_URL']
    result_url = settings.PAYBOX['RESULT_URL']
    success_url = settings.PAYBOX['SUCCESS_URL']
    failure_url = settings.PAYBOX['FAILURE_URL']
    testing_mode = settings.PAYBOX['TESTING_MODE']
    script = urlparse(payment_url).path[1:]
    salt = settings.SECRET_KEY

    params = {
        'pg_merchant_id': merchant_id,
        'pg_amount': amount,
        'pg_description': description,
        'pg_order_id': order_id,
        'pg_salt': salt,
        'pg_result_url': result_url,
        'pg_success_url': success_url,
        'pg_failure_url': failure_url,
        'pg_testing_mode': testing_mode,
    }
    params['pg_sig'] = sign(script, secret_key, params)

    data = do_request(payment_url, params)
    data['response']['pg_order_id'] = order_id

    return data


def get_order_status(order_id):

    merchant_id = settings.PAYBOX['MERCHANT_ID']
    secret_key = settings.PAYBOX['SECRET_KEY']
    status_url = settings.PAYBOX['STATUS_URL']
    script = urlparse(status_url).path[1:]
    salt = settings.SECRET_KEY

    params = {
        'pg_merchant_id': merchant_id,
        'pg_order_id': order_id,
        'pg_salt': salt,
    }
    params['pg_sig'] = sign(script, secret_key, params)

    data = do_request(status_url, params)

    return data


def set_callback(request):

    if request.method == 'POST':
        # convert query string to dictionary
        data = dict(parse_qsl(request.body.decode('utf-8')))
        # get transaction result
        result = data['pg_result']
        # check result: 1 - success, 0 - fail
        if int(result) == 1:
            product_id = data['pg_order_id'].split(':')[0]
            pay_by_id(product_id)
        else:
            # has error
            return 1

    return 0
