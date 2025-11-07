import json
from django.http import JsonResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.template.loader import render_to_string
from django.shortcuts import get_object_or_404, render, redirect
from django.db.models import Q

from naya_site.models import Product, CategoriaGaleria, ImagemGaleria


def index(request):
    categorias = CategoriaGaleria.objects.filter(ativa=True)
    imagens_list = ImagemGaleria.objects.filter(
        ativa=True).order_by('ordem', '-data_upload')

    # Paginação inicial
    paginator = Paginator(imagens_list, 8)
    page = request.GET.get('page', 1)

    try:
        imagens = paginator.page(page)
    except:
        imagens = paginator.page(1)

    context = {
        'site_title': 'Home',
        'categorias': categorias,
        'imagens': imagens,
        'categoria_atual': 'todos',
    }

    return render(request, 'naya_site/index.html', context)


def stock(request):
    products = Product.objects \
        .order_by('name')

    paginator = Paginator(products, 10)

    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'site_title': 'Produtos - ',
    }

    return render(
        request,
        'naya_site/stock.html',
        context
    )


def product(request, product_id):
    single_product = get_object_or_404(Product, pk=product_id)

    site_title = f'{single_product.name} -'

    context = {
        'product': single_product,
        'site_title': site_title,
    }

    return render(
        request,
        'naya_site/product.html',
        context
    )


def search(request):
    search_value = request.GET.get('q', '').strip()

    if search_value == '':
        return redirect('naya_site:index')

    products = Product.objects \
        .filter(
            Q(name__icontains=search_value)
        ) \
        .order_by('-name')

    paginator = Paginator(products, 10)

    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'site_title': 'Search - ',
    }

    return render(
        request,
        'naya_site/stock.html',
        context
    )


def carregar_galeria_ajax(request):
    try:
        categorias = CategoriaGaleria.objects.filter(ativa=True)
        categoria_filtro = request.GET.get('categoria', 'todos')
        pagina = request.GET.get('page', 1)

        imagens_list = ImagemGaleria.objects.filter(
            ativa=True).order_by('ordem', '-data_upload')

        if categoria_filtro and categoria_filtro != 'todos':
            imagens_list = imagens_list.filter(
                categoria__slug=categoria_filtro)

        # Paginação
        paginator = Paginator(imagens_list, 8)
        try:
            imagens = paginator.page(pagina)
        except PageNotAnInteger:
            imagens = paginator.page(1)
        except EmptyPage:
            imagens = paginator.page(paginator.num_pages)

        # Verificar se o template existe
        template_path = 'naya_site/partials/galeria_content.html'

        # Renderizar apenas o conteúdo da galeria
        context = {
            'imagens': imagens,
            'categorias': categorias,
            'categoria_atual': categoria_filtro,
        }

        html_galeria = render_to_string(template_path, context)

        response_data = {
            'html': html_galeria,
            'pagina_atual': imagens.number,
            'total_paginas': paginator.num_pages,
            'categoria_atual': categoria_filtro,
            'status': 'success'
        }

        return JsonResponse(response_data)

    except Exception as e:
        import traceback
        error_details = traceback.format_exc()

        return JsonResponse({
            'status': 'error',
            'message': str(e),
            'error_details': error_details
        }, status=500)
