from django.conf.urls import url

from .views import CarsView, ReregistrationView, DeregistrationView, RegistrationView, DocumentView

urlpatterns = [
    url(r'^$', CarsView.as_view()),
    url(r'^reregistration', ReregistrationView.as_view()),
    url(r'^deregistration', DeregistrationView.as_view()),
    url(r'^registration', RegistrationView.as_view()),
    url(r'^document/(?P<doc_id>[0-9a-f]*)', DocumentView.as_view())
]
