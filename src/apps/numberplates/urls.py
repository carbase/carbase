from django.conf.urls import url

from .views import NumberPlatesView, PersonNumberPlatesView


urlpatterns = [
    url(r'^$', NumberPlatesView.as_view()),
    url(r'^person$', PersonNumberPlatesView.as_view())
]
