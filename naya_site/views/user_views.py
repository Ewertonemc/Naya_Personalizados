# flake8: noqa: E501
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.forms import formset_factory
from django.db import transaction
from naya_site.models import Orcamento, ArquivoOrcamento, Product, StatusOrcamento
from naya_site.forms import OrcamentoForm, ItemOrcamentoForm, RespostaOrcamentoForm
from django.contrib.auth.models import User
from django.db.models import Count, Prefetch
from naya_site.utils import gerar_pdf_os


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
        item_formset = ItemFormSet(request.POST, request.FILES, prefix='itens')

        if orcamento_form.is_valid() and item_formset.is_valid():
            try:
                with transaction.atomic():
                    # Salvar orçamento
                    orcamento = orcamento_form.save(commit=False)
                    orcamento.cliente = request.user
                    orcamento.save()

                    # Salvar itens
                    itens_salvos = 0
                    for form in item_formset:
                        if form.cleaned_data and not form.cleaned_data.get(
                            'DELETE', False
                        ):
                            item = form.save(commit=False)
                            item.orcamento = orcamento

                            if not item.produto:
                                messages.error(
                                    request,
                                    'Selecione um produto válido.'
                                )
                                return redirect('naya_site:criar_orcamento')

                            item.save()
                            itens_salvos += 1

                            arquivos = form.cleaned_data.get('arquivos', [])
                            for arquivo in arquivos:
                                if arquivo is not None and hasattr(
                                    arquivo, 'name'
                                ):
                                    ArquivoOrcamento.objects.create(
                                        item_orcamento=item,
                                        arquivo=arquivo,
                                        tipo='cliente',
                                        nome_original=arquivo.name
                                    )
                                else:
                                    print(
                                        f"⚠️ Arquivo None ignorado no item {
                                            itens_salvos
                                        }"
                                    )

                    if itens_salvos == 0:
                        messages.error(
                            request, 'Adicione pelo menos um produto.')
                        orcamento.delete()
                        return redirect('naya_site:criar_orcamento')

                    messages.success(
                        request, 'Orçamento solicitado com sucesso!')
                    return redirect('naya_site:dashboard')

            except Exception as e:
                messages.error(request, f'Erro ao criar orçamento: {str(e)}')
                print(f"Erro ao criar orçamento: {e}")

        else:
            messages.error(request, 'Por favor, corrija os erros abaixo.')

    else:
        orcamento_form = OrcamentoForm()
        item_formset = ItemFormSet(prefix='itens')

    context = {
        'orcamento_form': orcamento_form,
        'item_formset': item_formset,
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
            # Muda para APROVADO (não diretamente para EM_PRODUCAO)
            orcamento.status = StatusOrcamento.APROVADO
            orcamento.save()
            messages.success(
                request,
                'Orçamento aprovado! Aguarde a confirmação da produção.'
            )

        elif acao == 'rejeitar':
            orcamento.status = StatusOrcamento.REJEITADO
            orcamento.save()
            messages.info(request, 'Orçamento rejeitado.')

        elif acao == 'alterar':
            observacoes = request.POST.get('observacoes_alteracao')
            orcamento.observacoes_cliente = observacoes
            orcamento.status = StatusOrcamento.AGUARDANDO_RESPOSTA
            orcamento.save()
            messages.info(request, 'Solicitação de alteração enviada.')

        return redirect(
            'naya_site:detalhe_orcamento',
            orcamento_id=orcamento_id
        )

    context = {
        'orcamento': orcamento,
    }
    return render(request, 'naya_site/responder_orcamento.html', context)


@login_required
def iniciar_producao(request, orcamento_id):
    """Staff muda orçamento para 'Em Produção'"""
    if not request.user.is_staff:
        messages.error(request, 'Acesso negado.')
        return redirect('naya_site:dashboard_orcamentos')

    orcamento = get_object_or_404(Orcamento, id=orcamento_id)

    if orcamento.status != StatusOrcamento.APROVADO:
        messages.error(
            request, 'Apenas orçamentos aprovados podem entrar em produção.')
        return redirect('naya_site:admin_dashboard')

    if request.method == 'POST':
        orcamento.status = StatusOrcamento.EM_PRODUCAO
        orcamento.save()
        messages.success(request, 'Orçamento movido para produção!')
        return redirect('naya_site:admin_dashboard')

    context = {
        'orcamento': orcamento,
    }
    return render(request, 'naya_site/confirmar_producao.html', context)


def get_produto_info(request, produto_id):
    """API para obter informações do produto"""
    try:
        produto = Product.objects.get(id=produto_id)

        # Construir URL absoluta da imagem
        if produto.image:
            imagem_url = request.build_absolute_uri(produto.image.url)
        else:
            imagem_url = request.build_absolute_uri('/static/img/no-image.png')

        data = {
            'nome': produto.name,
            'categoria': produto.category.name if produto.category else 'Sem categoria',
            'imagem': imagem_url,  # URL ABSOLUTA
            'preco_base': float(produto.unit_value),
        }
        return JsonResponse(data)

    except Product.DoesNotExist:
        return JsonResponse({'error': 'Produto não encontrado'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# Views para administração (empresa)


@login_required
def admin_dashboard(request):
    """Dashboard administrativo"""
    if not request.user.is_staff:
        messages.error(request, 'Acesso negado.')
        return redirect('naya_site:dashboard')

    # Clientes
    clientes = User.objects.filter(is_staff=False, is_superuser=False)

    aguardando_resposta = Orcamento.objects.filter(
        status=StatusOrcamento.AGUARDANDO_RESPOSTA).count()
    aguardando_cliente = Orcamento.objects.filter(
        status=StatusOrcamento.AGUARDANDO_CLIENTE).count()
    aprovados = Orcamento.objects.filter(
        status=StatusOrcamento.APROVADO).count()
    em_producao = Orcamento.objects.filter(
        status=StatusOrcamento.EM_PRODUCAO).count()
    finalizados = Orcamento.objects.filter(
        status=StatusOrcamento.FINALIZADO).count()

    # Orçamentos por status
    orcamentos_aguardando = Orcamento.objects.filter(
        status=StatusOrcamento.AGUARDANDO_RESPOSTA)
    orcamentos_cliente = Orcamento.objects.filter(
        status=StatusOrcamento.AGUARDANDO_CLIENTE)
    orcamentos_aprovados = Orcamento.objects.filter(
        status=StatusOrcamento.APROVADO)
    orcamentos_producao = Orcamento.objects.filter(
        status=StatusOrcamento.EM_PRODUCAO)
    orcamentos_finalizados = Orcamento.objects.filter(
        status=StatusOrcamento.FINALIZADO)

    # Estatísticas
    clientes_com_orcamento = clientes.filter(
        orcamento__isnull=False).distinct().count()
    total_orcamentos = Orcamento.objects.count()
    media_orcamentos = total_orcamentos / \
        clientes.count() if clientes.count() > 0 else 0

    context = {
        'aguardando_resposta': Orcamento.objects.filter(status=StatusOrcamento.AGUARDANDO_RESPOSTA).count(),
        'aguardando_cliente': Orcamento.objects.filter(status=StatusOrcamento.AGUARDANDO_CLIENTE).count(),
        'aprovados': Orcamento.objects.filter(status=StatusOrcamento.APROVADO).count(),
        'em_producao': em_producao,
        'finalizados': finalizados,
        'orcamentos_aguardando': Orcamento.objects.filter(status=StatusOrcamento.AGUARDANDO_RESPOSTA),
        'orcamentos_cliente': Orcamento.objects.filter(status=StatusOrcamento.AGUARDANDO_CLIENTE),
        'orcamentos_aprovados': Orcamento.objects.filter(status=StatusOrcamento.APROVADO),
        'orcamentos_producao': orcamentos_producao,
        'orcamentos_finalizados': orcamentos_finalizados,
        'clientes': clientes,
        'clientes_com_orcamento': clientes_com_orcamento,
        'total_orcamentos': total_orcamentos,
        'media_orcamentos': media_orcamentos,
    }
    return render(request, 'naya_site/admin_dashboard.html', context)


@login_required
def admin_responder_orcamento(request, orcamento_id):
    """Administrador responde ao orçamento"""
    if not request.user.is_staff:
        messages.error(request, 'Acesso negado.')
        return redirect('naya_site:dashboard_orcamentos')

    orcamento = get_object_or_404(Orcamento, id=orcamento_id)

    if request.method == 'POST':
        orcamento_form = RespostaOrcamentoForm(
            request.POST, instance=orcamento)

        # Processar itens
        valor_total = 0
        for item in orcamento.itens.all():  # type: ignore
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
            return redirect('naya_site:admin_dashboard')
    else:
        orcamento_form = RespostaOrcamentoForm(instance=orcamento)

    context = {
        'orcamento': orcamento,
        'orcamento_form': orcamento_form,
    }
    return render(request, 'naya_site/admin_responder.html', context)


@login_required
def criar_ordem_servico(request, orcamento_id):
    """Criar e visualizar ordem de serviço"""
    if not request.user.is_staff:
        messages.error(request, 'Acesso negado.')
        return redirect('naya_site:dashboard')

    orcamento = get_object_or_404(Orcamento, id=orcamento_id)
    if orcamento.status != StatusOrcamento.APROVADO and not orcamento.ordem_servico_criada:
        messages.error(
            request, 'Apenas orçamentos aprovados podem gerar ordem de serviço.')
        return redirect('naya_site:admin_dashboard')

    if request.method == 'POST':
        # Criar ordem de serviço
        if not orcamento.ordem_servico_criada:
            orcamento.criar_ordem_servico()
            print(f"OS Criada - Número: {orcamento.numero_os}")  # DEBUG
            messages.success(
                request, f'Ordem de serviço {orcamento.numero_os} criada com sucesso!')

        # Concluir produção
        acao = request.POST.get('acao')
        if acao == 'concluir':
            observacoes = request.POST.get('observacoes_producao', '')
            orcamento.observacoes_producao = observacoes
            orcamento.concluir_producao()
            messages.success(
                request, f'Produção da OS {orcamento.numero_os} concluída!')
            return redirect('naya_site:admin_dashboard')

    context = {
        'orcamento': orcamento,
    }
    return render(request, 'naya_site/ordem_servico.html', context)


@login_required
def download_pdf_os(request, orcamento_id):
    """View para download do PDF da OS"""
    if not request.user.is_staff:
        messages.error(request, 'Acesso negado.')
        return redirect('naya_site:dashboard')

    orcamento = get_object_or_404(Orcamento, id=orcamento_id)

    if not orcamento.ordem_servico_criada:
        messages.error(request, 'Ordem de serviço não criada.')
        return redirect('naya_site:admin_dashboard')

    try:
        # Gerar PDF
        buffer = gerar_pdf_os(orcamento)

        # Configurar resposta
        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="OS_{orcamento.numero_os}.pdf"'

        return response

    except Exception as e:
        messages.error(request, f'Erro ao gerar PDF: {str(e)}')
        return redirect('naya_site:criar_ordem_servico', orcamento_id=orcamento.id)
