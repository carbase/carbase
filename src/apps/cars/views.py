import xml.etree.ElementTree as ET

from django.http import JsonResponse, QueryDict
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from wkhtmltopdf.views import PDFTemplateView, PDFTemplateResponse

from .api import get_cars_by_iin, get_email_by_iin, get_cars_by_bin
from .models import Reregistration, Car, Deregistration, Agreement

from carbase.decorators import login_required
from carbase.helpers import send_mail
from controller.models import Center, Inspection
from numberplates.models import NumberPlate
from numberplates.views import get_number_plates


@method_decorator(login_required, name='dispatch')
@method_decorator(csrf_exempt, name='dispatch')
class CarsView(View):
    def get(self, request):
        if request.session.get('user_organizationalUnitName'):
            cars = get_cars_by_bin(request.session.get('user_organizationalUnitName'))
            own_agreements = Agreement.objects.filter(owner=request.session.get('user_organizationalUnitName'))
        else:
            cars = get_cars_by_iin(request.session.get('user_serialNumber'))
            own_agreements = []
        template_data = {
            'cars': cars,
            'own_agreements': own_agreements,
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
class DeregistrationView(View):
    def post(self, request):
        car = Car.objects.get(id=request.POST.get('car_id'))
        exist_degistrations = Deregistration.objects.filter(car=car)
        if exist_degistrations:
            deregistration = exist_degistrations[0]
            deregistration.is_transit_number = bool(request.POST.get('is_transit_number'))
            deregistration.is_paid = bool(request.POST.get('is_paid'))
            deregistration.save()
        else:
            deregistration = Deregistration.objects.create(
                is_transit_number=bool(request.POST.get('is_transit_number')),
                car=car,
                is_paid=bool(request.POST.get('is_paid')),
                is_success=False
            )
        return JsonResponse({'deregistration_id': deregistration.id, 'car_id': deregistration.car.id})

    def put(self, request):
        request.PUT = QueryDict(request.body)
        deregistration_id = request.PUT.get('deregistrationId')
        deregistration = Deregistration.objects.get(id=deregistration_id)
        if request.PUT.get('inspectionDate'):
            inspections = Inspection.objects.filter(deregistration=deregistration)
            if len(inspections):
                inspection = inspections[0]
            else:
                inspection = Inspection.objects.create(deregistration=deregistration)
            inspection.time_range = request.PUT.get('inspectionTimeRange')
            inspection.center_id = request.PUT.get('inspectionCenterId')
            inspection.date = request.PUT.get('inspectionDate')
            inspection.save()
        return JsonResponse({'deregistration_id': deregistration.id, 'car_id': deregistration.car.id})


@method_decorator(login_required, name='dispatch')
@method_decorator(csrf_exempt, name='dispatch')
class AgreementView(View):
    def post(self, request):
        car_id = request.POST.get('car_id')
        car = Car.objects.get(id=car_id)
        if request.session.get('user_organizationalUnitName'):
            seller = request.session.get('user_organizationalUnitName')
        else:
            seller = request.session.get('user_serialNumber')
        buyer = request.POST.get('buyer')
        agreement_id = request.POST.get('agreement')
        exist_registrations = Reregistration.objects.filter(car=car, buyer=buyer, seller=seller)
        if exist_registrations:
            reregistration = exist_registrations[0]
        else:
            reregistration = Reregistration.objects.create(car=car, buyer=buyer, seller=seller)
        if agreement_id != 'default':
            agreement = Agreement.objects.get(id=agreement_id)
            reregistration.agreement = agreement
            reregistration.save()
        return JsonResponse({'reregistration_id': reregistration.id})

    def delete(self, request):
        reregistration_id = QueryDict(request.body).get('reregistrationId')
        reregistration = Reregistration.objects.get(id=reregistration_id)
        user_sn = request.session.get('user_serialNumber')
        if request.session.get('user_organizationalUnitName'):
            user_sn = request.session.get('user_organizationalUnitName')
        if reregistration.buyer == user_sn or reregistration.seller == user_sn:
            reregistration.delete()
            return JsonResponse({'result': 'success'})
        else:
            return JsonResponse({'result': 'error'})

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
