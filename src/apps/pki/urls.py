from django.conf.urls import url
from .views import LoginView, LogoutView, change_email_address

urlpatterns = [
    url(r'^login/$', LoginView.as_view()),
    url(r'^logout/$', LogoutView.as_view()),
    url(r'^emailAddress/$', change_email_address)
]
