# flake8: noqa
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required


from naya_site.forms import ProductForm
from naya_site.models import Product


@login_required(login_url='naya_site:login')
def create(request):
    form_action = reverse('naya_site:create')

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)

        context = {
            'form': form,
            'form_action': form_action,
        }

        if form.is_valid():
            product = form.save(commit=False)
            product.save()
            return redirect('naya_site:update', product_id=product.pk)

        return render(
            request,
            'naya_site/create.html',
            context
        )

    context = {
        'form': ProductForm(),
        'form_action': form_action,
    }

    return render(
        request,
        'naya_site/create.html',
        context
    )


@login_required(login_url='naya_site:login')
def update(request, product_id):
    product = get_object_or_404(Product, pk=product_id,)

    form_action = reverse('naya_site:update', args=(product_id,))

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)

        context = {
            'form': form,
            'form_action': form_action,
        }

        print("FILES:", request.FILES)
        if form.is_valid():
            product = form.save()
            return redirect('naya_site:update', product_id=product.pk)

        return render(
            request,
            'naya_site/create.html',
            context
        )

    context = {
        'form': ProductForm(instance=product),
        'form_action': form_action,
    }

    return render(
        request,
        'naya_site/create.html',
        context
    )


@login_required(login_url='naya_site:login')
def delete(request, product_id):
    product = get_object_or_404(
        Product, pk=product_id,
    )

    confirmation = request.POST.get('confirmation', 'no')

    if confirmation == 'yes':
        product.delete()
        return redirect('naya_site:stock')

    return render(
        request,
        'naya_site/product.html',
        {
            'product': product,
            'confirmation': confirmation,
        }
    )
