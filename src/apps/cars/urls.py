from django.conf.urls import url

from .views import CarsView, AgreementView

urlpatterns = [
    url(r'^$', CarsView.as_view()),
    url(r'^agreement$', AgreementView.as_view())
]
