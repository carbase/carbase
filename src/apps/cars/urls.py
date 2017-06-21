from django.conf.urls import url

from .views import CarsView, AgreementView, AgreementPDFView
from .views import checkout, payment_status, get_numbers

urlpatterns = [
    url(r'^$', CarsView.as_view()),
    url(r'^agreement$', AgreementView.as_view()),
    url(r'^agreement/(?P<agreement_id>\d+)', AgreementPDFView.as_view()),
    url(r'^numbers$', get_numbers),
    url(r'^checkout$', checkout),
    url(r'^payment_status$', payment_status)
]
