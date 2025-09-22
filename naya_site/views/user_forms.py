from django.contrib import auth, messages
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from naya_site.forms import RegisterForm, RegisterUpdateForm


def register(request):
    form = RegisterForm()

    if request.method == 'POST':
        form = RegisterForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, 'Usuário registrado')
            return redirect('naya_site:index')

    return render(
        request,
        'naya_site/register.html',
        {
            'form': form,
        }
    )


def login_view(request):
    form = AuthenticationForm(request)

    if request.method == 'POST':
        form = AuthenticationForm(request, request.POST)

        if form.is_valid():
            user = form.get_user()
            auth.login(request, user)
            messages.success(request, 'Logado com Sucesso')
            return redirect('naya_site:index')
        messages.error(request, 'Login inválido')

    return render(
        request,
        'naya_site/login.html',
        {
            'form': form,
        }
    )


@login_required(login_url='naya_site:login')
def user_update(request):
    form = RegisterUpdateForm(instance=request.user)

    if request.method != 'POST':
        return render(
            request,
            'naya_site/user_update.html',
            {
                'form': form
            }
        )

    form = RegisterUpdateForm(data=request.POST, instance=request.user)

    if not form.is_valid():
        return render(
            request,
            'naya_site/user_update.html',
            {
                'form': form
            }
        )
    form.save()
    return redirect('contact:user_update')


@login_required(login_url='naya_site:login')
def logout_view(request):
    auth.logout(request)
    return redirect('naya_site:login')
