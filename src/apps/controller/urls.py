from django.conf.urls import url
from .views import login, logout, IndexView, InspectionView

urlpatterns = [
    url(r'^$', IndexView.as_view()),
    url(r'^inspection/$', InspectionView.as_view()),
    url(r'^login/$', login),
    url(r'^logout/$', logout)
]
