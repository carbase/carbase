from django.conf.urls import url

from .views import CarsView

urlpatterns = [
    url(r'^$', CarsView.as_view())
]
