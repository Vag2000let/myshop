from django.urls import path, re_path
import basketapp.views as basketapp

app_name = 'basketapp'

urlpatterns = [
    re_path(r'^index/$', basketapp.index, name='index'),
    re_path(r'^add/(?P<pk>\d+)/$', basketapp.basket_add, name='add'),
    re_path(r'^delete/(?P<pk>\d+)/$', basketapp.basket_delete, name='delete'),
    re_path(r'^update/(?P<pk>\d+)/(?P<quantity>\d+)/$', basketapp.basket_update, name='update'),
]
