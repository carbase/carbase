from django.conf.urls import url, include
from django.conf import settings
from django.contrib import admin
from django.views.generic import TemplateView

import debug_toolbar


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^cars/', include('cars.urls')),
    url(r'^pki/', include('pki.urls')),
    url(r'^payment/', include('payment.urls')),
    url(r'^controller/', include('controller.urls')),
    url(r'^numberplates/', include('numberplates.urls')),
    url(r'^$', TemplateView.as_view(template_name="index.html"))
]

if settings.DEBUG:
    urlpatterns = [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
