import xml.etree.ElementTree as ET
from math import floor

from django.http import JsonResponse, QueryDict
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views import View

from wkhtmltopdf.views import PDFTemplateView

from .api import get_cars_by_iin
from .models import Reregistration, Car, Tax, Fine

from carbase.decorators import login_required
from controller.models import Center, Inspection
# , set_number_plate_owner
from numberplates.views import get_number_plates
from payment.api import get_checkout_url, get_order_status


@method_decorator(login_required, name='dispatch')
class CarsView(View):
    def get(self, request):
        template_data = {
            'cars': get_cars_by_iin(request.session.get('user_serialNumber')),
            'reregistrations': Reregistration.objects.filter(
                buyer=request.session.get('user_serialNumber'),
                is_number_received=False
            ),
            'centers': Center.objects.all(),
            'owned_numbers': get_number_plates(owner_id=request.session.get('user_serialNumber')[3:]),
            'available_numbers': get_number_plates()
        }
        return render(request, 'cars/list.html', template_data)


class AgreementPDFView(PDFTemplateView):
    def get_context_data(self, **kwargs):
        context = super(AgreementPDFView, self).get_context_data(**kwargs)
        context['reregistration'] = Reregistration.objects.get(id=kwargs['agreement_id'])
        return context

    show_content_in_browser = True
    template_name = 'cars/agreement-pdf.html'


@method_decorator(login_required, name='dispatch')
class AgreementView(View):
    def post(self, request):
        car_id = request.POST.get('car_id')
        car = Car.objects.get(id=car_id)
        seller = request.session.get('user_serialNumber')
        buyer = request.POST.get('buyer')
        exist_registrations = Reregistration.objects.filter(car=car, buyer=buyer, seller=seller)
        if (exist_registrations):
            reregistration = exist_registrations[0]
        else:
            reregistration = Reregistration.objects.create(car=car, buyer=buyer, seller=seller)
        return JsonResponse({'reregistration_id': reregistration.id})

    def put(self, request):
        request.PUT = QueryDict(request.body)
        reregistration_id = request.PUT.get('reregistrationId')
        reregistration = Reregistration.objects.get(id=reregistration_id)
        if request.PUT.get('seller_sign'):
            reregistration.seller_sign = self.get_sign(request.PUT.get('seller_sign'))
            reregistration.amount = request.PUT.get('amount')
        if request.PUT.get('buyer_sign'):
            reregistration.buyer_sign = self.get_sign(request.PUT.get('buyer_sign'))
        if request.PUT.get('is_tax_paid'):
            reregistration.is_tax_paid = True
        if request.PUT.get('inspectionDate'):
            inspections = Inspection.objects.filter(reregistration=reregistration)
            if len(inspections):
                inspection = inspections[0]
            else:
                inspection = Inspection.objects.create(reregistration=reregistration)
            inspection.time_range = request.PUT.get('inspectionTimeRange')
            inspection.center_id = request.PUT.get('inspectionCenterId')
            inspection.date = request.PUT.get('inspectionDate')
            inspection.save()
        reregistration.save()
        return JsonResponse({
            'reregistration_id': reregistration.id,
            'seller_sign': reregistration.seller_sign,
            'buyer_sign': reregistration.buyer_sign
        })

    def get_sign(self, xml):
        xml_root = ET.fromstring(xml)
        return xml_root[2][1].text.strip()


@login_required
def checkout(request):
    product_id = request.GET.get('product_id')
    if product_id.startswith('tax'):
        Model = Tax
        entity_id = product_id[3:]
    elif product_id.startswith('fine'):
        Model = Fine
        entity_id = product_id[4:]

    if product_id.startswith('reg'):
        parameters = {
            'product_id': product_id,
            'amount': 11458.45,
            'order_desc': 'За выпуск СРТС и ГРНЗ'
        }
    else:
        entity = Model.objects.get(id=entity_id)
        parameters = {
            'product_id': product_id,
            'amount': floor(entity.amount),
            'order_desc': entity.info
        }

    checkout = get_checkout_url(parameters)
    return JsonResponse(checkout)


@login_required
def payment_status(request):
    order_id = request.GET.get('order_id')
    order_info = get_order_status(order_id)
    if order_info['response']['pg_transaction_status'] == 'ok':
        product_id = order_id.split(':')[0]
        if product_id.startswith('tax'):
            Model = Tax
            entity_id = product_id[3:]
        elif product_id.startswith('fine'):
            Model = Fine
            entity_id = product_id[4:]
        else:
            Model = Reregistration
            entity_id = product_id[3:]
        entity = Model.objects.get(id=entity_id)
        entity.is_paid = True
        entity.is_tax_paid = True
        entity.save()
    return JsonResponse(order_info)
