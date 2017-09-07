from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.x509 import NameOID

from datetime import datetime
import xml.etree.cElementTree as ET

from django.contrib import auth
from django.db.models import Q
from django.http import JsonResponse, QueryDict
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from .models import Inspector, Inspection, Center
from pki.models import RevokedCertificate


class IndexView(View):
    def get(self, request):
        ''' Главная страница со списком всех проверок '''
        template_data = {
            'is_allower': request.user.username.startswith('all'),
            'is_revisor': request.user.username.startswith('rev'),
            'is_admin': request.user.username.startswith('adm'),
        }
        inspections = []
        if request.user.is_authenticated:
            inspector = Inspector.objects.get(user=request.user)
            q = request.GET.get('q')
            if q:
                # Если страницу запросили с поисковым запросом
                inspections = Inspection.objects.filter(
                    Q(reregistration__buyer__icontains=q) |
                    Q(reregistration__seller__icontains=q) |
                    Q(reregistration__car__number__icontains=q) |
                    Q(reregistration__car__vin_code__icontains=q) |
                    Q(reregistration__car__manufacturer__icontains=q) |
                    Q(reregistration__car__model__icontains=q) |
                    Q(deregistration__car__user__icontains=q) |
                    Q(deregistration__car__number__icontains=q) |
                    Q(deregistration__car__vin_code__icontains=q) |
                    Q(deregistration__car__manufacturer__icontains=q) |
                    Q(deregistration__car__model__icontains=q)
                )
            else:
                # Иначе все заявки для этого спеццона
                inspections = Inspection.objects.filter(center=inspector.center)
                if inspector.role != 'admin':
                    # Если это не админ исключить завершенные заявки
                    inspections.exclude(is_success=True)
        template_data['inspections'] = inspections
        return render(request, 'controller/index.html', template_data)


def login(request):
    ''' Авторизация по ЭЦП '''
    signed_xml = request.POST.get('sign', '')
    try:
        # Парсим блок с информации о сертификате
        root = ET.fromstring(signed_xml)
        pem = '-----BEGIN CERTIFICATE-----\n'
        pem += list(root.iter('{http://www.w3.org/2000/09/xmldsig#}X509Certificate'))[0].text.strip()
        pem += '\n-----END CERTIFICATE-----'
        cert = x509.load_pem_x509_certificate(pem.encode('utf-8'), default_backend())
        certIssuerCN = cert.issuer.get_attributes_for_oid(NameOID.COMMON_NAME)[0].value
        # Проверяем не отозван ли сертификат, кто выдал сертификат и время действия сертификата
        revocked_cert_count = RevokedCertificate.objects.filter(serial_number=cert.serial_number).count()
        if (revocked_cert_count):
            raise ValueError('Сертификат отозван центром сертификации')
        if certIssuerCN != 'ҰЛТТЫҚ КУӘЛАНДЫРУШЫ ОРТАЛЫҚ (RSA)':
            raise ValueError('Ошибка проверки центра сертификации')
        if not (datetime.now() > cert.not_valid_before and datetime.now() < cert.not_valid_after):
            raise ValueError('Время действия сертификата истекло')
        user = None
        for cert_attr in cert.subject:
            if cert_attr.oid._name == 'serialNumber':
                user = auth.models.User.objects.get_or_create(username=cert_attr.value)[0]
                break
        else:
            raise ValueError('Ошибка проверки сертификата')
        center = Center.objects.get(id=1)
        Inspector.objects.get_or_create(user=user, center=center, role='all')
        auth.login(request, user)
    except ET.ParseError as err:
        return JsonResponse({'status': 'error', 'error_text': 'Ошибка проверки сертификата'})
    except ValueError as err:
        return JsonResponse({'status': 'error', 'error_text': err.args[0]})
    return JsonResponse({'status': 'success'})


def logout(request):
    auth.logout(request)
    return redirect('/controller')


@method_decorator(csrf_exempt, name='dispatch')
class InspectionView(View):
    def put(self, request):
        ''' Сюда приходят подтверждения или отказы в ходе проверки'''
        request.PUT = QueryDict(request.body)
        inspection = Inspection.objects.get(id=request.PUT.get('id'))
        if request.PUT.get('prelimenary_result'):
            # Предварительная проверка
            inspection.prelimenary_result = request.PUT.get('prelimenary_result')
            inspection.is_prelimenary_success = bool(int(request.PUT.get('is_prelimenary_success')))
            inspection.prelimenary_sign = request.PUT.get('sign')
            inspection.allower = request.user.inspector
        if request.PUT.get('revision_result'):
            # Сверка номеров
            inspection.is_revision_success = bool(int(request.PUT.get('is_revision_success')))
            inspection.revision_result = request.PUT.get('revision_result')
            inspection.revision_sign = request.PUT.get('sign')
            inspection.revisor = request.user.inspector
        if request.PUT.get('is_success'):
            # Заключительная проверка
            if inspection.reregistration:
                inspection.reregistration.car.user = inspection.reregistration.buyer
                inspection.reregistration.car.number = inspection.reregistration.number
                inspection.reregistration.car.is_registred = True
                inspection.reregistration.car.save()
                inspection.reregistration.is_number_received = True
                inspection.reregistration.save()
            if inspection.deregistration:
                inspection.deregistration.car.is_registred = False
                inspection.deregistration.car.save()
                inspection.deregistration.is_success = True
                inspection.deregistration.save()
            inspection.is_success = bool(int(request.PUT.get('is_success')))
        if request.PUT.get('result'):
            inspection.result = request.PUT.get('result')
            inspection.sign = request.PUT.get('sign')
        inspection.save()
        return JsonResponse({'result': 'success'})
