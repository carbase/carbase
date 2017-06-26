from django.conf.urls import url

from .views import get_numbers

urlpatterns = [
    url(r'^numbers$', get_numbers)
]
