from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^register/$', views.RegisterView.as_view(), name='register'),
    url(r'^usernames/(?P<username>[a-zA-Z0-9_-]{5,20})/$', views.UsernameCountView.as_view(), name='usernamecount'),
    url(r'^mobiles/(?P<mobile>1[3-9]\d{9})/$', views.MobileCountView.as_view(), name='mobilecount'),
    url(r'^login/$', views.LoginView.as_view(), name='login'),
    url(r'^logout/$', views.LogoutView.as_view(), name='logout'),
    url(r'^center/$', views.UserCenterInfoView.as_view(), name='center'),
    url(r'^emails/$', views.EmailView.as_view(), name='emails'),
    url(r'^emailsactive/$', views.EmailActiveView.as_view(), name='emailsactive'),
    url(r'^addresses/$', views.AddressView.as_view(), name='addresses'),
    url(r'^addresses/create/$', views.CreateAddressView.as_view(), name='create'),
    url(r'^addresses/(?P<address_id>\d+)/default/$', views.DefaultAddressView.as_view(), name='default'),
    url(r'^addresses/(?P<address_id>\d+)/$', views.UpdateDstroyAddressView.as_view(), name='update'),
    url(r'^addresses/(?P<address_id>\d+)/title/$', views.UpdateTitleAddressView.as_view(), name='title'),
    url(r'^pass/$', views.UpdatePasswordView.as_view(), name='password'),

]