from django.conf.urls import url

from .views import CarsView, AgreementView, AgreementPDFView

urlpatterns = [
    url(r'^$', CarsView.as_view()),
    url(r'^agreement$', AgreementView.as_view()),
    url(r'^agreement/(?P<agreement_id>\d+)', AgreementPDFView.as_view())
]
