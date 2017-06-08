from django.shortcuts import render, redirect
from django.views import View
from .api import get_cars_by_iin
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, QueryDict
import xml.etree.ElementTree as ET

from .models import Reregestration, Car, Tax, Fine

from payment.api import get_checkout_url, get_order_status


class CarsView(View):
    def get(self, request):
        print(not request.session.get('user_serialNumber'))
        if not request.session.get('user_serialNumber'):
            return redirect('/')
        cars = get_cars_by_iin(request.session.get('user_serialNumber'))
        reregistrations = Reregestration.objects.filter(buyer=request.session.get('user_serialNumber'))
        return render(request, 'cars/list.html', {'cars': cars, 'reregistrations': reregistrations})


@method_decorator(csrf_exempt, name='dispatch')
class AgreementView(View):
    def post(self, request):
        car_id = request.POST.get('car_id')
        car = Car.objects.get(id=car_id)
        seller = request.session.get('user_serialNumber')
        buyer = request.POST.get('buyer')
        exist_registrations = Reregestration.objects.filter(car=car, buyer=buyer, seller=seller)
        if (exist_registrations):
           reregestration = exist_registrations[0]
        else:
           reregestration = Reregestration.objects.create(car=car, buyer=buyer, seller=seller)
        return JsonResponse({'reregistration_id': reregestration.id})

    def put(self, request):
        request.PUT = QueryDict(request.body)
        reregistration_id = request.PUT.get('reregistrationId')
        reregistration = Reregestration.objects.get(id=reregistration_id)
        if request.PUT.get('seller_sign'):
            reregistration.seller_sign = self.get_sign(request.PUT.get('seller_sign'))
            reregistration.amount = request.PUT.get('amount')
        if request.PUT.get('buyer_sign'):
            reregistration.buyer_sign = self.get_sign(request.PUT.get('buyer_sign'))
        if request.PUT.get('is_tax_paid'):
            reregistration.is_tax_paid = True
        if request.PUT.get('inspection_time'):
            reregistration.inspection_time = request.PUT.get('inspection_time')
        # reregistration.save()
        return JsonResponse({
            'reregistration_id': reregistration.id,
            'seller_sign': reregistration.seller_sign,
            'buyer_sign': reregistration.buyer_sign
        })

    def get_sign(self, xml):
        xml_root = ET.fromstring(xml)
        return xml_root[2][1].text.strip()


def checkout(request):
    product_id = request.GET.get('product_id')
    if product_id.startswith('tax'):
        Model = Tax
        entity_id = product_id[3:]
    elif product_id.startswith('fine'):
        Model = Fine
        entity_id = product_id[4:]
    else:
        Model = Reregestration
        entity_id = product_id[3:]



    if product_id.startswith('reg'):
        parameters = {
            'product_id': product_id,
            'amount': 1145845,
            'order_desc': 'За выпуск СРТС и ГРНЗ'
        }
    else:
        entity = Model.objects.get(id=entity_id)
        parameters = {
            'product_id': product_id,
            'amount': int(entity.amount * 100),
            'order_desc': entity.info
        }

    checkout = get_checkout_url(parameters)
    return JsonResponse(checkout)

def payment_status(request):
    order_id = request.GET.get('order_id')
    order_info = get_order_status(order_id)
    product_id = order_info['response']['order_id'].split('_')[0]
    if product_id.startswith('tax'):
        Model = Tax
        entity_id = product_id[3:]
    elif product_id.startswith('fine'):
        Model = Fine
        entity_id = product_id[4:]
    else:
        Model = Reregestration
        entity_id = product_id[3:]
    entity = Model.objects.get(id=entity_id)
    entity.is_paid = True
    entity.is_tax_paid = True
    entity.save()
    return JsonResponse(order_info)
