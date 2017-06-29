from math import floor

from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from carbase.helpers import http_code
from carbase.decorators import login_required
from cars.models import Reregistration, Tax, Fine, Deregistration
from numberplates.models import NumberPlate
from .api import set_callback, get_checkout_url, get_order_status


@csrf_exempt
def callback(request):

    invoke = set_callback(request)

    if invoke == 0:
        return http_code('OK', 200)

    return http_code('Not Approved', 200)


@login_required
def checkout(request):
    product_id = request.GET.get('product_id')

    if product_id.startswith('reg'):
        reregistration = Reregistration.objects.get(id=product_id[3:])
        reg_amount = 11458.45
        if reregistration.number and reregistration.number != 'RANDOM':
            num_str = reregistration.number
            number = NumberPlate.objects.get(digits=num_str[0:3], characters=num_str[3:6], region=num_str[6:])
            if not number.is_sold:
                reg_amount = number.get_price()
        parameters = {
            'product_id': product_id,
            'amount': reg_amount,
            'order_desc': 'За выпуск СРТС и ГРНЗ'
        }
    elif product_id.startswith('num'):
        number = NumberPlate.objects.get(id=product_id[3:])
        parameters = {
            'product_id': product_id,
            'amount': floor(number.get_price()),
            'order_desc': 'Покупка номера ' + str(number)
        }
    elif product_id.startswith('fine'):
        fine = Tax.objects.get(id=product_id[4:])
        parameters = {
            'product_id': product_id,
            'amount': floor(fine.amount),
            'order_desc': fine.info
        }
    elif product_id.startswith('tax'):
        tax = Tax.objects.get(id=product_id[3:])
        parameters = {
            'product_id': product_id,
            'amount': floor(tax.amount),
            'order_desc': tax.info
        }
    elif product_id.startswith('tran'):
        tax = Deregistration.objects.get(id=product_id[4:])
        parameters = {
            'product_id': product_id,
            'amount': floor(settings.MCI * 0.3),
            'order_desc': 'Транзитные номера для снятия с учета'
        }
        print(parameters)

    checkout = get_checkout_url(parameters)
    return JsonResponse(checkout)


@login_required
def payment_status(request):
    order_id = request.GET.get('order_id')
    order_info = get_order_status(order_id)
    if order_info['response']['pg_transaction_status'] == 'ok':
        product_id = order_id.split(':')[0]
        if product_id.startswith('tax'):
            model = Tax
            entity_id = product_id[3:]
        elif product_id.startswith('fine'):
            model = Fine
            entity_id = product_id[4:]
        elif product_id.startswith('num'):
            model = NumberPlate
            entity_id = product_id[3:]
        elif product_id.startswith('tran'):
            model = Deregistration
            entity_id = product_id[4:]
        else:
            model = Reregistration
            entity_id = product_id[3:]
        entity = model.objects.get(id=entity_id)
        if product_id.startswith('num'):
            entity.set_owner(request.session.get('user_serialNumber')[3:])
        entity.is_paid = True
        entity.is_tax_paid = True
        entity.save()
    return JsonResponse(order_info)
