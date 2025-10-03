from django.contrib import auth, messages
from django.contrib.auth import login

from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from naya_site.forms import RegisterForm, RegisterUpdateForm
from naya_site.models import UserProfile, State


def register(request):
    form = RegisterForm()

    if request.method == 'POST':
        form = RegisterForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)
            user.save()

            state_code = form.cleaned_data.get('state')
            state_instance = State.objects.get(
                name=state_code) if state_code else None

            UserProfile.objects.create(
                user=user,
                cpf=form.cleaned_data['cpf'],
                cep=form.cleaned_data['cep'],
                logradouro=form.cleaned_data['logradouro'],
                numero=form.cleaned_data['numero'],
                complemento=form.cleaned_data['complemento'],
                bairro=form.cleaned_data['bairro'],
                cidade=form.cleaned_data['cidade'],
                state=state_instance
            )

            login(request, user)
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


def perfil(request):
    single_user = request.user

    site_title = f'{single_user} -'

    context = {
        'user': single_user,
        'site_title': site_title,
    }

    return render(
        request,
        'naya_site/perfil.html',
        context
    )


@login_required(login_url='naya_site:login')
def user_update(request):

    user = request.user

    if request.method == 'POST':
        form = RegisterUpdateForm(
            data=request.POST,
            instance=user
        )

        if form.is_valid():
            form.save()
            messages.success(request, 'Perfil atualizado com sucesso!')
            return redirect('naya_site:perfil')
        else:
            messages.error(request, 'Por favor, corrija os erros abaixo.')
    else:
        form = RegisterUpdateForm(instance=user)

    return render(
        request,
        'naya_site/user_update.html',
        {
            'form': form
        }
    )


@login_required(login_url='naya_site:login')
def logout_view(request):
    auth.logout(request)
    return redirect('naya_site:login')
