from django.contrib import auth
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from authapp.forms import ShopUserRegisterForm, ShopUserLoginForm, ShopUserUpdateForm
from django.core.mail import send_mail
from django.conf import settings
from authapp.models import ShopUser
from authapp.forms import ShopUserProfileUpdateForm
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.dispatch import receiver
from django.db.models.signals import pre_save
from django.db import connection





def login(request):
    # print(f'GET: {request.GET}')
    next = request.GET['next'] if 'next' in request.GET.keys() else None

    if request.method == 'POST':
        form = ShopUserLoginForm(data=request.POST)
        if form.is_valid():
            username = request.POST['username']
            password = request.POST['password']
            user = auth.authenticate(username=username, password=password)
            if user and user.is_active:
                next = request.POST['next'] if 'next' in request.POST.keys() else None
                # print(f'next: {next}')
                auth.login(request, user)
                return HttpResponseRedirect(reverse('main:index') if not next else next)
    else:
        form = ShopUserLoginForm()

    context = {
        'page_title': 'вход в личный кабинет',
        'form': form,
        'next': next,
    }
    return render(request, 'authapp/login.html', context)


def logout(request):
    auth.logout(request)
    return HttpResponseRedirect(reverse('main:index'))


def update(request):
    if request.method == 'POST':
        form = ShopUserUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('auth:update'))
    else:
        form = ShopUserUpdateForm(instance=request.user)

    context = {'page_title': 'редактирование',
               'form': form}
    return render(request, 'authapp/update.html', context)


def send_verify_mail(user):
    verify_link = reverse('auth:verify', args=[user.email, user.activation_key])

    title = f'Подтверждение учетной записи {user.username}'

    message = f'Для подтверждения учетной записи {user.username} \
    на портале {settings.DOMAIN_NAME} перейдите по ссылке: \
    \n{settings.DOMAIN_NAME}{verify_link}'

    print(f'from: {settings.EMAIL_HOST_USER}, to: {user.email}')

    return send_mail(
            title,
            message,
            settings.EMAIL_HOST_USER,
            [user.email],
            fail_silently=False
        )


def verify(request, email, activation_key):
    try:
        user = ShopUser.objects.get(email=email)
        if user.activation_key == activation_key and not user.is_activation_key_expired():
            user.is_active = True
            user.save()
            auth.login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return render(request, 'authapp/verification.html')
        else:
            print(f'error activation user: {user}')
            return render(request, 'authapp/verification.html')
    except Exception as e:
        print(f'error activation user: {e.args}')
    return HttpResponseRedirect(reverse('main:index'))



def register(request):
    title = 'регистрация'

    if request.method == 'POST':
        register_form = ShopUserRegisterForm(request.POST, request.FILES)
        if register_form.is_valid():
            user = register_form.save()
            if send_verify_mail(user):
                print('сообщение подтверждения отправлено')
                return HttpResponseRedirect(reverse('auth:login'))
            else:
                print('ошибка отправки сообщения')
                return HttpResponseRedirect(reverse('auth:login'))
    else:
        register_form = ShopUserRegisterForm()

    context = {
        'page_title': title,
        'register_form': register_form
    }
    return render(request, 'authapp/register.html', context)


@login_required
@transaction.atomic
def update(request):
    title = 'редактирование'

    if request.method == 'POST':
        form = ShopUserUpdateForm(request.POST, request.FILES, instance=request.user)
        profile_form = ShopUserProfileUpdateForm(request.POST, instance=request.user.shopuserprofile)
        if form.is_valid() and profile_form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('auth:update'))
    else:
        form = ShopUserUpdateForm(instance=request.user)
        profile_form = ShopUserProfileUpdateForm(instance=request.user.shopuserprofile)

    context = {
        'page_title': title,
        'form': form,
        'profile_form': profile_form
    }

    return render(request, 'authapp/update.html', context)

