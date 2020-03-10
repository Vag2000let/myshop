from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse, reverse_lazy
from adminapp.forms import ShopUserAdminCreateForm, ShopUserAdminUpdateForm
from authapp.models import ShopUser
from django.utils.decorators import method_decorator
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from mainapp.models import ProductCategory, Product
from adminapp.forms import ProductCategoryAdminUpdateForm, ProductAdminUpdateForm
from django.dispatch import receiver
from django.db.models.signals import pre_save
from django.db import connection




# @user_passes_test(lambda x: x.is_superuser)
# def index(request):
#     object_list = ShopUser.objects.all()
#
#     context = {
#         'page_title': 'админка/пользователи',
#         'object_list': object_list,
#     }
#     return render(request, 'adminapp/index.html', context)



class ShopUserListView(ListView):
    model = ShopUser
    # template_name = 'adminapp/index.html'
    @method_decorator(user_passes_test(lambda x: x.is_superuser))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


@user_passes_test(lambda x: x.is_superuser)
def shopuser_create(request):
    if request.method == 'POST':
        form = ShopUserAdminCreateForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('adminapp:index'))
    else:
        form = ShopUserAdminCreateForm()

    context = {
        'page_title': 'админка/новый пользователь',
        'form': form
    }

    return render(request, 'adminapp/shopuser_update.html', context)


@user_passes_test(lambda x: x.is_superuser)
def shopuser_update(request, pk):
    user = get_object_or_404(ShopUser, pk=pk)
    if request.method == 'POST':
        form = ShopUserAdminUpdateForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('adminapp:index'))
    else:
        form = ShopUserAdminUpdateForm(instance=user)

    context = {
        'page_title': 'админка/редактирование пользователя',
        'form': form
    }

    return render(request, 'adminapp/shopuser_update.html', context)


@user_passes_test(lambda x: x.is_superuser)
def shopuser_delete(request, pk):
    user = get_object_or_404(ShopUser, pk=pk)
    if request.method == 'POST':
        user.is_active = False
        user.save()

        return HttpResponseRedirect(reverse('adminapp:index'))
    elif request.method == 'GET':
        context = {
            'page_title': 'админка/удаление пользователя',
            'object': user,
        }
        return render(request, 'adminapp/shopuser_delete.html', context)


@user_passes_test(lambda x: x.is_superuser)
def shopuser_recovery(request, pk):
    # Восстановление пользователя
    user = get_object_or_404(ShopUser, pk=pk)
    if request.method == 'POST':
        user.is_active = True
        user.save()

        return HttpResponseRedirect(reverse('adminapp:index'))
    elif request.method == 'GET':
        context = {
            'page_title': 'админка/восстановление пользователя',
            'object': user,
        }

        return render(request, 'adminapp/shopuser_recovery.html', context)


@user_passes_test(lambda x: x.is_superuser)
def productcategory_list(request):
    object_list = ProductCategory.objects.all()
    context = {
        'page_title': 'админка/категории',
        'object_list': object_list
    }

    return render(request, 'adminapp/productcategory_list.html', context)


# @user_passes_test(lambda x: x.is_superuser)
# def productcategory_create(request):
#     if request.method == 'POST':
#         form = ProductCategoryAdminUpdateForm(request.POST, request.FILES)
#         if form.is_valid():
#             form.save()
#             return HttpResponseRedirect(reverse('myadmin:productcategory_list'))
#     else:
#         form = ProductCategoryAdminUpdateForm()
#
#     context = {
#         'page_title': 'админка/новая категория товара',
#         'form': form
#     }
#
#     return render(request, 'adminapp/productcategory_update.html', context)

class ProductCategoryCreateView(CreateView):
    model = ProductCategory
    success_url = reverse_lazy('myadmin:productcategory_list')
    # fields = '__all__'
    form_class = ProductCategoryAdminUpdateForm


# @user_passes_test(lambda x: x.is_superuser)
# def productcategory_update(request, pk):
#     productcategory = get_object_or_404(ProductCategory, pk=pk)
#     if request.method == 'POST':
#         form = ProductCategoryAdminUpdateForm(request.POST, request.FILES, instance=productcategory)
#         if form.is_valid():
#             form.save()
#             return HttpResponseRedirect(reverse('myadmin:productcategory_list'))
#     else:
#         form = ProductCategoryAdminUpdateForm(instance=productcategory)
#
#     context = {
#         'page_title': 'админка/редактирование категории товара',
#         'form': form
#     }
#
#     return render(request, 'adminapp/productcategory_update.html', context)


class ProductCategoryUpdateView(UpdateView):
    model = ProductCategory
    template_name = 'adminapp/productcategory_update.html'
    success_url = reverse_lazy('myadmin:productcategory_list')
    form_class = ProductCategoryAdminUpdateForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'админка/редактирование категории товара'

        return context

    def form_valid(self, form):
        if 'discount' in form.cleaned_data:
            discount = form.cleaned_data['discount']
            if discount:
                self.object.product_set.update(price=F('price') * (1 - discount / 100))
                db_profile_by_type(self.__class__, 'UPDATE', connection.queries)

        return super().form_valid(form)


# @user_passes_test(lambda x: x.is_superuser)
# def productcategory_delete(request, pk):
#     productcategory = get_object_or_404(ProductCategory, pk=pk)
#     if request.method == 'POST':
#         productcategory.is_active = False
#         productcategory.save()
#         return HttpResponseRedirect(reverse('myadmin:productcategory_list'))
#     elif request.method == 'GET':
#         context = {
#             'page_title': 'админка/удаление категории',
#             'object': productcategory,
#         }
#         return render(request, 'adminapp/productcategory_delete.html', context)


class ProductCategoryDeleteView(DeleteView):
    model = ProductCategory
    success_url = reverse_lazy('myadmin:productcategory_list')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.is_active = False
        self.object.save()

        return HttpResponseRedirect(self.get_success_url())


@user_passes_test(lambda x: x.is_superuser)
def productcategory_products(request, pk):
    # товары категории
    productcategory = get_object_or_404(ProductCategory, pk=pk)
    context = {
        'page_title': 'админка/товары категории',
        'productcategory': productcategory,
        'object_list': productcategory.product_set.all()
    }

    return render(request, 'adminapp/product_list.html', context)


@user_passes_test(lambda x: x.is_superuser)
def product_create(request, pk):
    productcategory = get_object_or_404(ProductCategory, pk=pk)
    if request.method == 'POST':
        form = ProductAdminUpdateForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('myadmin:productcategory_products',
                                                kwargs={'pk': pk}))
    else:
        form = ProductAdminUpdateForm(initial={'category': productcategory})

    context = {
        'page_title': 'админка/новый товар',
        'form': form,
        'object': productcategory
    }

    return render(request, 'adminapp/product_update.html', context)


@user_passes_test(lambda x: x.is_superuser)
def product_update(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductAdminUpdateForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('myadmin:productcategory_products',
                                                kwargs={'pk': product.category.pk}))
    else:
        form = ProductAdminUpdateForm(instance=product)

    context = {
        'page_title': 'админка/редактирование товара',
        'form': form,
        'object': product.category
    }

    return render(request, 'adminapp/product_update.html', context)


@user_passes_test(lambda x: x.is_superuser)
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)

    if request.method == 'POST':
        product.is_active = False
        product.save()
        return HttpResponseRedirect(reverse('myadmin:productcategory_products',
                                            kwargs={'pk': product.category.pk}))
    elif request.method == 'GET':
        context = {
            'page_title': 'админка/удаление продукта',
            'object': product,
        }
        return render(request, 'adminapp/product_delete.html', context)


# @user_passes_test(lambda x: x.is_superuser)
# def product_read(request, pk):
#     product = get_object_or_404(Product, pk=pk)
#     context = {
#         'page_title': 'админка/продукт подробно',
#         'object': product
#     }
#
#     return render(request, 'adminapp/product_read.html', context)


class ProductDetailView(DetailView):
    model = Product

# «.update()


def db_profile_by_type(prefix, type, queries):
    update_queries = list(filter(lambda x: type in x['sql'], queries))
    print(f'db_profile {type} for {prefix}:')
    [print(query['sql']) for query in update_queries]


@receiver(pre_save, sender=ProductCategory)
def product_is_active_update_productcategory_save(sender, instance, **kwargs):
    if instance.pk:
        if instance.is_active:
            instance.product_set.update(is_active=True)
        else:
            instance.product_set.update(is_active=False)

        db_profile_by_type(sender, 'UPDATE', connection.queries)

