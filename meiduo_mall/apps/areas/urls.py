from . import views
from django.conf.urls import url

urlpatterns = [
    url(r'^areas/$', views.AreasView.as_view(), name='areas'),
]
