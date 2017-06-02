from django.conf import settings

from urllib.request import HTTPError, URLError

from .helpers import create_signature, create_guid, post_data, request_to_json
from cars.api import pay_by_id


def get_exception(code, reason):
    return {
        'response': {
            'response_status': 'failure',
            'error_code': str(code),
            'error_message': str(reason),
        }
    }


def do_request(url, params):
    try:
        data = post_data(url, {'request': params})
        return data
    except HTTPError as ex:
        return get_exception(ex.code, ex.reason)
    except URLError as ex:
        return get_exception(400, ex.reason)


def get_checkout_url(parameters):

    product_id = parameters['product_id']
    amount = parameters['amount']
    order_desc = parameters['order_desc']
    order_id = '{}_{}'.format(product_id, create_guid())

    params = {
        'order_id':             order_id,
        'order_desc':           order_desc,
        'amount':               amount,
        'product_id':           product_id,
        'server_callback_url':  settings.PAYMENT_GATEWAYS['FONDY']['SERVER_CALLBACK_URL'],
        'currency':             settings.PAYMENT_GATEWAYS['FONDY']['CURRENCY'],
        'merchant_id':          settings.PAYMENT_GATEWAYS['FONDY']['MERCHANT_ID'],
        'lifetime':             settings.PAYMENT_GATEWAYS['FONDY']['LIFETIME'],
        'lang':                 settings.PAYMENT_GATEWAYS['FONDY']['LANG'],
    }
    params['signature'] = create_signature(settings.PAYMENT_GATEWAYS['FONDY']['TRANSACTION_PASSWORD'], params)

    url = settings.PAYMENT_GATEWAYS['FONDY']['CHECKOUT_URL']
    data = do_request(url, params)
    data['response']['order_id'] = order_id

    return data


def get_order_status(order_id):

    merchant_id = settings.PAYMENT_GATEWAYS['FONDY']['MERCHANT_ID']
    transaction_password = settings.PAYMENT_GATEWAYS['FONDY']['TRANSACTION_PASSWORD']

    params = {
        'order_id':     order_id,
        'merchant_id':  merchant_id,
    }
    params['signature'] = create_signature(transaction_password, params)

    url = settings.PAYMENT_GATEWAYS['FONDY']['STATUS_URL']
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
