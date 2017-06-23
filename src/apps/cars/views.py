import xml.etree.ElementTree as ET
from math import floor

from django.contrib.humanize.templatetags.humanize import intcomma
from django.http import JsonResponse, QueryDict
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from wkhtmltopdf.views import PDFTemplateView, PDFTemplateResponse

from .api import get_cars_by_iin, get_email_by_iin
from .models import Reregistration, Car, Tax, Fine

from carbase.decorators import login_required
from carbase.helpers import send_mail
from controller.models import Center, Inspection
from numberplates.models import NumberPlate
from numberplates.views import get_number_plates
from payment.api import get_checkout_url, get_order_status


@method_decorator(login_required, name='dispatch')
@method_decorator(csrf_exempt, name='dispatch')
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
@method_decorator(csrf_exempt, name='dispatch')
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
        if request.PUT.get('number'):
            number = request.PUT.get('number')
            if number != 'RANDOM':
                number = NumberPlate.objects.get(id=number)
            reregistration.number = str(number)
        reregistration.save()
        is_sign_request = request.PUT.get('seller_sign') or request.PUT.get('buyer_sign')
        if reregistration.seller_sign and reregistration.buyer_sign and is_sign_request:
            emails = [get_email_by_iin(reregistration.buyer[3:]), get_email_by_iin(reregistration.seller[3:])]
            email_title = 'Договор купли/продажи'
            email_text = 'Договор купли/продажи находиться в приложении к письму'
            attach_filename = 'Договор купли/продажи.pdf'
            pdf_resp = PDFTemplateResponse(request, 'cars/agreement-pdf.html', {'reregistration': reregistration})
            attach_data = pdf_resp.rendered_content
            attach_mime = 'application/pdf'
            send_mail(email_title, email_text, emails, attach_filename, attach_data, attach_mime)
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
        elif product_id.startswith('num'):
            Model = NumberPlate
            entity_id = product_id[3:]
        else:
            Model = Reregistration
            entity_id = product_id[3:]
        entity = Model.objects.get(id=entity_id)
        if product_id.startswith('num'):
            entity.set_owner(request.session.get('user_serialNumber')[3:])
        entity.is_paid = True
        entity.is_tax_paid = True
        entity.save()
    return JsonResponse(order_info)


@login_required
def get_numbers(request):
    numbers = get_number_plates(search_pattern=request.GET.get('q'))
    numbers_list = []
    for number in numbers:
        numbers_list.append({
            'id': number.id,
            'digits': number.digits,
            'characters': number.characters,
            'region': number.region,
            'price': intcomma(number.get_price())
        })
    return JsonResponse(numbers_list, safe=False)
