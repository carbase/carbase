import xml.etree.ElementTree as ET
import mimetypes

from bson import ObjectId
import gridfs
from pymongo import MongoClient

from django.conf import settings
from django.db.models import Q
from django.http import JsonResponse, QueryDict, HttpResponse
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from .models import Reregistration, Car, Deregistration, Registration
from .models import Agreement, Email, AgreementTemplate, Sign

from carbase.decorators import login_required
from controller.models import Center, Inspection
from numberplates.models import NumberPlate
from numberplates.views import get_number_plates


@method_decorator(login_required, name='dispatch')
@method_decorator(csrf_exempt, name='dispatch')
class CarsView(View):
    ''' Возвращает список машин физ лица, или, если есть БИН, то организации '''
    def get(self, request):
        user = request.session.get('user_organizationalUnitName')
        if not user:
            user = request.session.get('user_serialNumber')
        cars = Car.objects.filter(user=user).order_by('id')
        ''' Незаконченные перерегистрации где пользователь выступает в качестве покупателя '''
        reregistrations = Reregistration.objects.filter(buyer=user, is_number_received=False)

        template_data = {
            'cars': cars,
            'reregistrations': reregistrations,
            'owned_numbers': get_number_plates(owner_id=request.session.get('user_serialNumber')[3:]),
            'available_numbers': get_number_plates()
        }
        return render(request, 'cars/list.html', template_data)


@method_decorator(login_required, name='dispatch')
class DocumentView(View):
    def get(self, request, doc_id):
        mongo_client = MongoClient(settings.MONGO_URL)
        mongo_fs = gridfs.GridFS(mongo_client.documents)
        doc = mongo_fs.get(ObjectId(doc_id))
        response = HttpResponse(doc.read(), content_type=mimetypes.guess_type(doc.filename))
        response['Content-Disposition'] = 'attachment; filename="' + doc_id + '.' + doc.filename.split('.')[-1] + '"'
        return response


@method_decorator(login_required, name='dispatch')
@method_decorator(csrf_exempt, name='dispatch')
class RegistrationView(View):
    def get(self, request):
        user = request.session.get('user_organizationalUnitName')
        if not user:
            user = request.session.get('user_serialNumber')
        try:
            registration = Registration.objects.get(user=user)
        except Registration.DoesNotExist:
            registration = None
        template_data = {
            'registration': registration,
            'owned_numbers': get_number_plates(owner_id=request.session.get('user_serialNumber')[3:]),
            'available_numbers': get_number_plates(),
            'centers': Center.objects.all(),
        }
        return render(request, 'cars/registration.html', template_data)

    def post(self, request):
        vin_code = request.POST.get('vin_code')
        if request.session.get('user_organizationalUnitName'):
            user = request.session.get('user_organizationalUnitName')
        else:
            user = request.session.get('user_serialNumber')
        try:
            registration = Registration.objects.get(user=user, car_vin_code=vin_code)
        except Registration.DoesNotExist:
            registration = Registration.objects.create(user=user, car_vin_code=vin_code)
        registration.upload_document(request.FILES.getlist('documents'))
        document_urls = registration.get_document_urls()
        return JsonResponse({'registration_id': registration.id, 'document_urls': document_urls})

    def put(self, request):
        request.PUT = QueryDict(request.body)
        registration_id = request.PUT.get('registrationId')
        registration = Registration.objects.get(id=registration_id)
        if request.PUT.get('is_tax_paid'):
            registration.is_tax_paid = True
        if request.PUT.get('inspectionDate'):
            inspections = Inspection.objects.filter(registration=registration)
            if len(inspections):
                inspection = inspections[0]
            else:
                inspection = Inspection.objects.create(registration=registration)
            inspection.time_range = request.PUT.get('inspectionTimeRange')
            inspection.center_id = request.PUT.get('inspectionCenterId')
            inspection.date = request.PUT.get('inspectionDate')
            inspection.save()
            return JsonResponse({
                'registration_id': registration.id,
                'time': inspection.time
            })
        if request.PUT.get('number'):
            number = request.PUT.get('number')
            if number != 'RANDOM':
                number = NumberPlate.objects.get(id=number)
            registration.number = str(number)
        registration.save()
        return JsonResponse({
            'registration_id': registration.id,
        })


@method_decorator(login_required, name='dispatch')
@method_decorator(csrf_exempt, name='dispatch')
class DeregistrationView(View):
    def get(self, request):
        user = request.session.get('user_organizationalUnitName')
        if not user:
            user = request.session.get('user_serialNumber')
        car_id = request.GET.get('car')
        try:
            deregistration = Deregistration.objects.get(car=car_id)
        except Deregistration.DoesNotExist:
            deregistration = None
        context = {
            'deregistration': deregistration,
            'centers': Center.objects.all(),
            'car_id': car_id
        }
        return render(request, 'cars/deregistration.html', context)

    def post(self, request):
        car = Car.objects.get(id=request.POST.get('car_id'))
        exist_degistrations = Deregistration.objects.filter(car=car)
        if exist_degistrations:
            deregistration = exist_degistrations[0]
            deregistration.is_transit_number = bool(int(request.POST.get('is_transit_number')))
            deregistration.is_paid = bool(int(request.POST.get('is_paid', '0')))
            deregistration.save()
        else:
            deregistration = Deregistration.objects.create(
                is_transit_number=bool(int(request.POST.get('is_transit_number'))),
                car=car,
                is_paid=bool(int(request.POST.get('is_paid', '0'))),
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
            return JsonResponse({
                'deregistration_id': deregistration.id,
                'time': inspection.time
            })
        return JsonResponse({'deregistration_id': deregistration.id, 'car_id': deregistration.car.id})


@method_decorator(login_required, name='dispatch')
@method_decorator(csrf_exempt, name='dispatch')
class ReregistrationView(View):
    def get(self, request):
        user = request.session.get('user_organizationalUnitName')
        if not user:
            user = request.session.get('user_serialNumber')
        car_id = request.GET.get('car')

        try:
            reregistration = Reregistration.objects.get(car=car_id, is_number_received=False)
        except Reregistration.DoesNotExist:
            reregistration = None

        if request.GET.get('side') == 'seller':
            agreements = AgreementTemplate.objects.filter(Q(owner=user) | Q(owner=None))
            context = {'reregistration': reregistration, 'agreements': agreements, 'car_id': car_id}
            return render(request, 'cars/reregistration_seller.html', context)
        else:
            context = {
                'owned_numbers': get_number_plates(owner_id=request.session.get('user_serialNumber')[3:]),
                'available_numbers': get_number_plates(),
                'reregistration': reregistration,
                'centers': Center.objects.all()
            }
            return render(request, 'cars/reregistration_buyer.html', context)

    def post(self, request):
        ''' Создания нового процесса перерегистрации '''
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
        agreement_template = AgreementTemplate.objects.get(id=agreement_id)
        agreement_context = {
            'seller': seller,
            'buyer': buyer,
            'car': '{} {}'.format(car.manufacturer, car.model)
        }
        agreement = Agreement.objects.create(template=agreement_template, context=agreement_context)
        reregistration.agreement = agreement
        reregistration.save()
        return JsonResponse({'reregistration_id': reregistration.id, 'agreement': agreement.render()})

    def delete(self, request):
        ''' Отказ от перерегистрации на этапе подписания договоров '''
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
            self.save_sign(reregistration.agreement, request.PUT.get('seller_sign'))
        if request.PUT.get('buyer_sign'):
            reregistration.buyer_sign = self.get_sign(request.PUT.get('buyer_sign'))
            self.save_sign(reregistration.agreement, request.PUT.get('buyer_sign'))
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
            return JsonResponse({
                'reregistration_id': reregistration.id,
                'time': inspection.time
            })
        if request.PUT.get('number'):
            number = request.PUT.get('number')
            if number != 'RANDOM':
                number = NumberPlate.objects.get(id=number)
            reregistration.number = str(number)
        reregistration.save()
        return JsonResponse({
            'reregistration_id': reregistration.id,
            'seller_sign': reregistration.seller_sign,
            'buyer_sign': reregistration.buyer_sign
        })

    def get_sign(self, xml):
        xml_root = ET.fromstring(xml)
        xml_sign = xml_root.find('{http://www.w3.org/2000/09/xmldsig#}Signature')
        sign_value = xml_sign.find('{http://www.w3.org/2000/09/xmldsig#}SignatureValue')
        return sign_value.text

    def save_sign(self, agreement, xml_sign):
        xml_root = ET.fromstring(xml_sign)
        xml_sign = xml_root.find('{http://www.w3.org/2000/09/xmldsig#}Signature')
        sign_value = ET.tostring(xml_sign.find('{http://www.w3.org/2000/09/xmldsig#}SignatureValue'))
        signed_info = ET.tostring(xml_sign.find('{http://www.w3.org/2000/09/xmldsig#}SignedInfo'))
        key_info = ET.tostring(xml_sign.find('{http://www.w3.org/2000/09/xmldsig#}KeyInfo'))
        Sign.objects.create(
            agreement=agreement,
            signature_value=sign_value,
            signed_info=signed_info,
            key_info=key_info
        )

    def get_email_by_iin(self, iin):
        try:
            email_obj = Email.objects.get(iin=iin)
            return email_obj.email
        except Email.DoesNotExist:
            pass
