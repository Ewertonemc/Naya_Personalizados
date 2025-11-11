# views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from naya_site.models import CategoriaGaleria, ImagemGaleria
from naya_site.forms import UploadImagemForm


def is_admin(user):
    return user.is_staff or user.is_superuser


@login_required
@user_passes_test(is_admin)
def gerenciar_galeria(request):
    categoria_id = request.GET.get('categoria')

    if categoria_id:
        imagens = ImagemGaleria.objects.filter(categoria_id=categoria_id)
        categoria_atual = int(categoria_id)
    else:
        imagens = ImagemGaleria.objects.all()
        categoria_atual = None

    context = {
        'imagens': imagens,
        'categorias': CategoriaGaleria.objects.all(),
        'categoria_atual': categoria_atual,
    }
    return render(request, 'naya_site/gerenciar_galeria.html', context)


@login_required
@user_passes_test(is_admin)
def upload_imagem(request):
    if request.method == 'POST':
        form = UploadImagemForm(request.POST, request.FILES)
        if form.is_valid():
            imagem = form.save()
            messages.success(
                request, f'Imagem "{imagem.descricao}" adicionada com sucesso!')
            return redirect('naya_site:gerenciar_galeria')
        else:
            messages.error(request, 'Por favor, corrija os erros abaixo.')
    else:
        form = UploadImagemForm()

    context = {
        'form': form,
        'site_title': 'Upload de Imagem',
    }

    return render(request, 'naya_site/upload_imagem.html', context)


@login_required
@user_passes_test(is_admin)
def deletar_imagem(request, imagem_id):
    try:
        imagem = ImagemGaleria.objects.get(id=imagem_id)
        descricao = imagem.descricao
        imagem.delete()
        messages.success(
            request, f'Imagem "{descricao}" deletada com sucesso!')
    except ImagemGaleria.DoesNotExist:
        messages.error(request, 'Imagem não encontrada.')

    return redirect('naya_site:gerenciar_galeria')


@login_required
@user_passes_test(is_admin)
def toggle_imagem(request, imagem_id):
    try:
        imagem = ImagemGaleria.objects.get(id=imagem_id)
        imagem.ativa = not imagem.ativa
        imagem.save()

        status = "ativada" if imagem.ativa else "desativada"
        messages.success(
            request, f'Imagem "{imagem.descricao}" {status} com sucesso!')
    except ImagemGaleria.DoesNotExist:
        messages.error(request, 'Imagem não encontrada.')

    return redirect('naya_site:gerenciar_galeria')
