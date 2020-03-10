from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, get_object_or_404
from basketapp.models import Basket
from django.template.loader import render_to_string
from django.urls import reverse
from mainapp.models import Product
from mainapp.views import get_basket



@login_required
def index(request):
    context = {
        'page_title': 'корзина',
        'basket': get_basket(request),
    }
    return render(request, 'basketapp/index.html', context)


@login_required
def basket_add(request, pk):
    if 'login' in request.META.get('HTTP_REFERER'):
        return HttpResponseRedirect(reverse('main:product', args=[pk]))

    product = get_object_or_404(Product, pk=pk)
    old_basket_item = Basket.get_product(user=request.user, product=product)

    if old_basket_item:
        # old_basket_item[0].quantity += 1
        old_basket_item[0].quantity = F('quantity') + 1
        old_basket_item[0].save()

        # update_queries = list(filter(lambda x: 'UPDATE' in x['sql'], connection.queries))
        # print(f'query basket_add: {update_queries}')
    else:
        new_basket_item = Basket(user=request.user, product=product)
        new_basket_item.quantity += 1
        new_basket_item.save()

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required
def basket_delete(request, pk):
    get_object_or_404(Basket, pk=pk).delete()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def basket_update(request, pk, quantity):
    if request.is_ajax():
        basket_obj = get_object_or_404(Basket, pk=pk)
        quantity = int(quantity)
        if quantity > 0:
            basket_obj.quantity = quantity
            basket_obj.save()
        else:
            basket_obj.delete()

        result = render_to_string('basketapp/includes/inc__basket_list.html',
                                  context={'basket': get_basket(request)})

        return JsonResponse({'result': result})
