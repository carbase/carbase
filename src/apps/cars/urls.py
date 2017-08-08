from django.conf.urls import url

from .views import CarsView, ReregistrationView, DeregistrationView

urlpatterns = [
    url(r'^$', CarsView.as_view()),
    url(r'^reregistration', ReregistrationView.as_view()),
    url(r'^deregistration', DeregistrationView.as_view()),
]
