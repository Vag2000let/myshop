import json
import random

from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import render, get_object_or_404

from mainapp.models import ProductCategory, Product
from django.conf import settings
from django.core.cache import cache

from django.template.loader import render_to_string
from django.views.decorators.cache import cache_page
from django.http import JsonResponse



def index(request):

    # products = Product.objects.filter(is_active=True, category__is_active=True)
    # products = Product.objects.filter(is_active=True, category__is_active=True).select_related('category')
    products = get_products()[:3]

    context = {
        'page_title': 'магазин гаджетов',
        'products': products,
        'main_catalog': get_main_catalog(),
        'hot_product': get_hot_product(),

    }
    return render(request, 'mainapp/index.html', context)


def get_main_catalog():
    return ProductCategory.objects.all()


def get_basket(request):
    if request.user.is_authenticated:
        return request.user.basket.all().order_by('product__category')
    else:
        return []


def get_hot_product():
    return random.choice(Product.objects.all())


def catalog(request):
    context = {
        'page_title': 'каталог',
        'main_catalog': get_main_catalog(),
        'hot_product': get_hot_product(),

    }
    return render(request, 'mainapp/catalog.html', context)


# Все Продукты
@cache_page(3600)
def category(request, pk, page=1):
    page_title = 'Все'
    pk = int(pk)

    links_menu = get_links_menu()

    if pk == 0:
        category = {
            'pk': 0,
            'name': 'Все',
        }
        # category_products = Product.objects.all()
        category_products = get_products_orederd_by_price()
    else:
        # category = get_object_or_404(ProductCategory, pk=pk)
        category = get_category(pk)

        # category_products = Product.objects.filter(category__pk=pk).order_by('price')
        category_products = get_products_in_category_orederd_by_price(pk)


    paginator = Paginator(category_products, 2)
    try:
        products_paginator = paginator.page(page)
    except PageNotAnInteger:
        products_paginator = paginator.page(1)
    except EmptyPage:
        products_paginator = paginator.page(paginator.num_pages)

    context = {
        'page_title': page_title,
        'category': category,
        'category_products': products_paginator,
        # 'main_catalog': get_main_catalog(),
        'main_catalog': links_menu,
    }
    return render(request, 'mainapp/category_catalog.html', context)


def product(request, pk):
    # product = get_object_or_404(Product, pk=pk)
    # product = get_object_or_404(Product, pk=pk).select_related()
    product = get_product(pk)


    context = {
        'page_title': 'страница продукта',
        'main_catalog': get_links_menu(),
        'category_products': product.category,
        'product': product,

    }
    return render(request, 'mainapp/product.html', context)


def contacts(request):
    # locations = [
    #     {
    #     'phone': '8-800-800-80-80',
    #     'email': 'gadgets@mail.ru',
    #     'address': 'ул. Сущёвский Вал, 5, стр. 1'
    #     }
    # ]
    #
    # with open('myshop/locations.json', 'w', encoding='utf-8') as f:
    #     json.dump(locations, f)

    with open('mainapp/json/locations.json', 'r', encoding='utf-8') as f:
        locations = json.load(f)


    context = {
        'page_title': 'контакты',
        'locations': locations,
    }
    return render(request, 'mainapp/contacts.html', context)


# Кеширование

def get_links_menu():
    if settings.LOW_CACHE:
        key = 'links_menu'
        links_menu = cache.get(key)
        if links_menu is None:
           links_menu = ProductCategory.objects.filter(is_active=True)
           cache.set(key, links_menu)
        return links_menu
    else:
        return ProductCategory.objects.filter(is_active=True)


def get_category(pk):

    if settings.LOW_CACHE:
        key = f'category_{pk}'
        category = cache.get(key)
        if category is None:
            category = get_object_or_404(ProductCategory, pk=pk)
            cache.set(key, category)
        return category
    else:
        return get_object_or_404(ProductCategory, pk=pk)


def get_products():
    if settings.LOW_CACHE:
        key = 'products'
        products = cache.get(key)
        if products is None:
            products = Product.objects.filter(is_active=True, \
                                             category__is_active=True).select_related('category')
            cache.set(key, products)
        return products
    else:
        return Product.objects.filter(is_active=True, \
                                      category__is_active=True).select_related('category')


def get_product(pk):
    if settings.LOW_CACHE:
        key = f'product_{pk}'
        product = cache.get(key)
        if product is None:
            product = get_object_or_404(Product, pk=pk)
            cache.set(key, product)
        return product
    else:
        return get_object_or_404(Product, pk=pk)


def get_products_orederd_by_price():
    if settings.LOW_CACHE:
        key = 'products_orederd_by_price'
        products = cache.get(key)
        if products is None:
            products = Product.objects.filter(is_active=True,
                                              category__is_active=True).order_by('price')
            cache.set(key, products)
        return products
    else:
        return Product.objects.filter(is_active=True,
                                      category__is_active=True).order_by('price')


def get_products_in_category_orederd_by_price(pk):
    if settings.LOW_CACHE:
        key = f'products_in_category_orederd_by_price_{pk}'
        products = cache.get(key)
        if products is None:
            products = Product.objects.filter(category__pk=pk, is_active=True,
                                              category__is_active=True).order_by('price')
            cache.set(key, products)
        return products
    else:
        return Product.objects.filter(category__pk=pk, is_active=True,
                                      category__is_active=True).order_by('price')


def products_ajax(request, pk=None, page=1):
    if request.is_ajax():
        links_menu = get_links_menu()

        if pk:
            if pk == '0':
                category = {
                   'pk': 0,
                   'name': 'все'
                }
                category_products = get_products_orederd_by_price()
            else:
                category = get_category(pk)
                category_products = get_products_in_category_orederd_by_price(pk)

                paginator = Paginator(category_products, 2)
            try:
                products_paginator = paginator.page(page)
            except PageNotAnInteger:
                products_paginator = paginator.page(1)
            except EmptyPage:
                products_paginator = paginator.page(paginator.num_pages)

            context = {
               'main_catalog': links_menu,
               'category': category,
               'category_products': products_paginator,
            }

            result = render_to_string(
                        'mainapp/includes/inc__category_catalog_list_content.html',
                        context=context,
                        request=request)

            return JsonResponse({'result': result})
