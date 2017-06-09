from django.conf.urls import url
from .views import login, logout, IndexView

urlpatterns = [
    url(r'^$', IndexView.as_view()),
    url(r'^login/$', login),
    url(r'^logout/$', logout)
]
