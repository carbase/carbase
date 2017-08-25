from math import floor

from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from carbase.helpers import http_code
from carbase.decorators import login_required
from cars.models import Reregistration, Tax, Fine, Deregistration, Registration
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
    if '|' in product_id:
        parameters = {
            'product_id': product_id,
            'amount': 0,
            'order_desc': ''
        }
        for prod_id in product_id.split('|'):
            if prod_id.startswith('fine'):
                fine = Fine.objects.get(id=prod_id[4:])
                parameters['amount'] += floor(fine.amount)
                parameters['order_desc'] += fine.info + '. '
            elif prod_id.startswith('tax'):
                tax = Tax.objects.get(id=prod_id[3:])
                parameters['amount'] += floor(tax.amount)
                parameters['order_desc'] += tax.info + '. '
    elif product_id.startswith('reg'):
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
    elif product_id.startswith('new'):
        registration = Registration.objects.get(id=product_id[3:])
        reg_amount = 11458.45
        if registration.number and registration.number != 'RANDOM':
            num_str = registration.number
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
        fine = Fine.objects.get(id=product_id[4:])
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

    checkout = get_checkout_url(parameters)
    return JsonResponse(checkout)


@login_required
def payment_status(request):
    order_id = request.GET.get('order_id')
    order_info = get_order_status(order_id)
    response = order_info['response']
    if 'pg_transaction_status' in response and response['pg_transaction_status'] == 'ok':
        product_id = order_id.split(':')[0]
        if '|' in product_id:
            for prod_id in product_id.split('|'):
                if prod_id.startswith('fine'):
                    fine = Fine.objects.get(id=prod_id[4:])
                    fine.is_paid = True
                    fine.save()
                elif prod_id.startswith('tax'):
                    tax = Tax.objects.get(id=prod_id[3:])
                    tax.is_paid = True
                    tax.save()
        elif product_id.startswith('reg'):
            reregistration = Registration.objects.get(id=product_id[3:])
            reregistration.is_tax_paid = True
            reregistration.save()
        elif product_id.startswith('new'):
            registration = Registration.objects.get(id=product_id[3:])
            registration.is_paid = True
            registration.save()
        elif product_id.startswith('num'):
            number = NumberPlate.objects.get(id=product_id[3:])
            number.set_owner(request.session.get('user_serialNumber')[3:])
            number.save()
        elif product_id.startswith('fine'):
            fine = Fine.objects.get(id=product_id[4:])
            fine.is_paid = True
            fine.save()
        elif product_id.startswith('tax'):
            tax = Tax.objects.get(id=product_id[3:])
            tax.is_paid = True
            tax.save()
        elif product_id.startswith('tran'):
            deregistration = Deregistration.objects.get(id=product_id[4:])
            deregistration.is_paid = True
            deregistration.save()
    return JsonResponse(order_info)
