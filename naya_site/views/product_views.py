from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render, redirect
from django.db.models import Q

from naya_site.models import Product


def index(request):
    context = {
        'site_title': 'Home',
    }

    return render(
        request,
        'naya_site/index.html',
        context
    )


def stock(request):
    products = Product.objects \
        .order_by('-id')

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
