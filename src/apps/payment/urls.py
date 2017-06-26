from django.conf.urls import url

from .views import callback, checkout, payment_status

urlpatterns = [
    url(r'^callback$', callback),
    url(r'^checkout$', checkout),
    url(r'^payment_status$', payment_status)
]
