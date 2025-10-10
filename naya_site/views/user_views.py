from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.forms import formset_factory
from django.db import transaction
from naya_site.models import Orcamento, ItemOrcamento, ArquivoOrcamento, Product, StatusOrcamento
from naya_site.forms import OrcamentoForm, ItemOrcamentoForm, RespostaOrcamentoForm, ItemRespostaForm


@login_required
def dashboard_orcamentos(request):
    """Dashboard principal do cliente"""
    orcamentos = Orcamento.objects.filter(cliente=request.user)

    # Status atual do cliente
    ultimo_orcamento = orcamentos.first()
    status_atual = ultimo_orcamento.status if ultimo_orcamento else 'sem_orcamento'

    context = {
        'orcamentos': orcamentos[:5],  # Últimos 5 orçamentos
        'status_atual': status_atual,
        'ultimo_orcamento': ultimo_orcamento,
    }
    return render(request, 'naya_site/dashboard.html', context)


@login_required
def criar_orcamento(request):
    """Criar novo orçamento"""
    ItemFormSet = formset_factory(ItemOrcamentoForm, extra=1, can_delete=True)

    if request.method == 'POST':
        orcamento_form = OrcamentoForm(request.POST)
        item_formset = ItemFormSet(request.POST, request.FILES)

        if orcamento_form.is_valid() and item_formset.is_valid():
            with transaction.atomic():
                orcamento = orcamento_form.save(commit=False)
                orcamento.cliente = request.user
                orcamento.save()

                for item_form in item_formset:
                    if item_form.cleaned_data and not item_form.cleaned_data.get('DELETE', False):
                        item = item_form.save(commit=False)
                        item.orcamento = orcamento
                        item.save()

                        # Salvar arquivos
                        arquivos = item_form.cleaned_data.get('arquivos', [])
                        for arquivo in arquivos:
                            ArquivoOrcamento.objects.create(
                                item_orcamento=item,
                                arquivo=arquivo,
                                tipo='cliente',
                                nome_original=arquivo.name
                            )

                messages.success(request, 'Orçamento solicitado com sucesso!')
                return redirect('dashboard_orcamentos')
    else:
        orcamento_form = OrcamentoForm()
        item_formset = ItemFormSet()

    context = {
        'orcamento_form': orcamento_form,
        'item_formset': item_formset,
        # 'product': Product.objects.filter(ativo=True),
    }
    return render(request, 'naya_site/criar_orcamento.html', context)


@login_required
def detalhe_orcamento(request, orcamento_id):
    """Visualizar detalhes do orçamento"""
    orcamento = get_object_or_404(
        Orcamento, id=orcamento_id, cliente=request.user)

    context = {
        'orcamento': orcamento,
    }
    return render(request, 'naya_site/detalhe_orcamento.html', context)


@login_required
def responder_orcamento(request, orcamento_id):
    """Cliente responde ao orçamento"""
    orcamento = get_object_or_404(
        Orcamento, id=orcamento_id, cliente=request.user)

    if orcamento.status != StatusOrcamento.AGUARDANDO_CLIENTE:
        messages.error(
            request, 'Este orçamento não está aguardando sua resposta.')
        return redirect('detalhe_orcamento', orcamento_id=orcamento_id)

    if request.method == 'POST':
        acao = request.POST.get('acao')

        if acao == 'aprovar':
            orcamento.status = StatusOrcamento.EM_PRODUCAO
            orcamento.save()
            messages.success(
                request, 'Orçamento aprovado! Seu pedido entrou em produção.')

        elif acao == 'rejeitar':
            orcamento.status = StatusOrcamento.REJEITADO
            orcamento.save()
            messages.info(request, 'Orçamento rejeitado.')

        elif acao == 'alterar':
            # Lógica para solicitar alterações
            observacoes = request.POST.get('observacoes_alteracao')
            orcamento.observacoes_cliente = observacoes
            orcamento.status = StatusOrcamento.AGUARDANDO_RESPOSTA
            orcamento.save()
            messages.info(request, 'Solicitação de alteração enviada.')

        return redirect('detalhe_orcamento', orcamento_id=orcamento_id)

    context = {
        'orcamento': orcamento,
    }
    return render(request, 'naya_site/responder_orcamento.html', context)


def get_produto_info(request, produto_id):
    """API para obter informações do produto"""
    try:
        produto = Product.objects.get(id=produto_id, ativo=True)
        data = {
            'nome': produto.name,
            'categoria': produto.category.name,
            'imagem': produto.image.url if produto.image else '',
            'preco_base': float(produto.price),
        }
        return JsonResponse(data)
    except Product.DoesNotExist:
        return JsonResponse({'error': 'Produto não encontrado'}, status=404)

# Views para administração (empresa)


@login_required
def admin_dashboard(request):
    """Dashboard administrativo"""
    if not request.user.is_staff:
        messages.error(request, 'Acesso negado.')
        return redirect('dashboard_orcamentos')

    # Contadores para cards
    aguardando_resposta = Orcamento.objects.filter(
        status=StatusOrcamento.AGUARDANDO_RESPOSTA).count()
    aguardando_cliente = Orcamento.objects.filter(
        status=StatusOrcamento.AGUARDANDO_CLIENTE).count()
    aprovados = Orcamento.objects.filter(
        status=StatusOrcamento.APROVADO).count()

    # Orçamentos por status
    orcamentos_aguardando = Orcamento.objects.filter(
        status=StatusOrcamento.AGUARDANDO_RESPOSTA)
    orcamentos_cliente = Orcamento.objects.filter(
        status=StatusOrcamento.AGUARDANDO_CLIENTE)
    orcamentos_aprovados = Orcamento.objects.filter(
        status=StatusOrcamento.APROVADO)

    context = {
        'aguardando_resposta': aguardando_resposta,
        'aguardando_cliente': aguardando_cliente,
        'aprovados': aprovados,
        'orcamentos_aguardando': orcamentos_aguardando,
        'orcamentos_cliente': orcamentos_cliente,
        'orcamentos_aprovados': orcamentos_aprovados,
    }
    return render(request, 'naya_site/admin_dashboard.html', context)


@login_required
def admin_responder_orcamento(request, orcamento_id):
    """Administrador responde ao orçamento"""
    if not request.user.is_staff:
        messages.error(request, 'Acesso negado.')
        return redirect('dashboard_orcamentos')

    orcamento = get_object_or_404(Orcamento, id=orcamento_id)

    if request.method == 'POST':
        orcamento_form = RespostaOrcamentoForm(
            request.POST, instance=orcamento)

        # Processar itens
        valor_total = 0
        for item in orcamento.itens.all():
            preco_unitario = request.POST.get(f'item_{item.id}_preco', 0)
            item.preco_unitario = float(
                preco_unitario) if preco_unitario else 0
            item.save()
            valor_total += item.preco_total

            # Processar arquivos da empresa
            arquivos_empresa = request.FILES.getlist(
                f'item_{item.id}_arquivos')
            for arquivo in arquivos_empresa:
                ArquivoOrcamento.objects.create(
                    item_orcamento=item,
                    arquivo=arquivo,
                    tipo='empresa',
                    nome_original=arquivo.name
                )

        if orcamento_form.is_valid():
            orcamento = orcamento_form.save(commit=False)
            orcamento.valor_total = valor_total
            orcamento.status = StatusOrcamento.AGUARDANDO_CLIENTE
            orcamento.save()

            messages.success(request, 'Resposta enviada ao cliente!')
            return redirect('admin_dashboard')
    else:
        orcamento_form = RespostaOrcamentoForm(instance=orcamento)

    context = {
        'orcamento': orcamento,
        'orcamento_form': orcamento_form,
    }
    return render(request, 'naya_site/admin_responder.html', context)
