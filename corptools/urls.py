from django.conf.urls import url

from . import views
from corptools.audit_views.character import assets, wallet, pub_data
app_name = 'corptools'

urlpatterns = [
    url(r'^$', views.corptools_menu, name='view'),
    url(r'^add_char/$', views.add_char, name='add_char'),
    url(r'^admin/$', views.admin, name='admin'),
    url(r'^assets/$', assets, name='assets'),
    url(r'^assets/(?P<character_id>(\d)*)/$', assets, name='assets'),
    url(r'^wallet/$', wallet, name='wallet'),
    url(r'^wallet/(?P<character_id>(\d)*)/$', wallet, name='wallet'),
    url(r'^overview/$', pub_data, name='overview'),
    url(r'^overview/(?P<character_id>(\d)*)/$', pub_data, name='overview')
    ]