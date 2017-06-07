from django.conf.urls import url

from .views import callback

urlpatterns = [
    url(r'^callback$', callback),
]