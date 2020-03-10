from django.urls import path, re_path
import mainapp.views as mainapp
from django.views.decorators.cache import cache_page

app_name = 'mainapp'

urlpatterns = [
    re_path(r'^$', mainapp.index, name='index'),
    re_path(r'^catalog/$', mainapp.catalog, name='catalog'),
    re_path(r'^category/(?P<pk>\d+)/$', mainapp.category, name='category'),
    # re_path(r'^category/(?P<pk>\d+)/ajax/$', cache_page(3600)(mainapp.products_ajax)),
    re_path(r'^category/(?P<pk>\d+)/(?P<page>\d+)/$', mainapp.category, name='category_paginator'),
    # re_path(r'^category/(?P<pk>\d+)/(?P<page>\d+)/ajax/$', cache_page(3600)(mainapp.products_ajax)),

    re_path(r'^product/(?P<pk>\d+)/$', mainapp.product, name='product'),
    re_path(r'^contacts/$', mainapp.contacts, name='contacts'),
]
