from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.x509 import NameOID

from datetime import datetime
import xml.etree.cElementTree as ET

from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from .models import RevokedCertificate


class LoginView(View):
    def post(self, request):
        signed_xml = request.POST.get('signedXml', '')
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
            for cert_attr in cert.subject:
                # Сохраняем атрибуты сертификата в сессию
                request.session['user_' + cert_attr.oid._name] = cert_attr.value
        except ET.ParseError as err:
            return JsonResponse({'status': 'error', 'error_text': 'Ошибка проверки сертификата'})
        except ValueError as err:
            return JsonResponse({'status': 'error', 'error_text': err.args[0]})
        return JsonResponse({'status': 'success'})


@method_decorator(csrf_exempt, name='dispatch')
class LogoutView(View):
    def post(self, request):
        request.session.flush()
        return JsonResponse({'status': 'success'})


def change_email_address(request):
    ''' Временная(пока не получим доступ к базе физ-лиц) ссылка для изменения имейла и телефона '''
    if request.POST.get('emailAddress'):
        request.session['user_emailAddress'] = request.POST.get('emailAddress')
    if request.POST.get('phoneNumber'):
        request.session['user_phoneNumber'] = request.POST.get('phoneNumber')
    return JsonResponse({'status': 'success'})
