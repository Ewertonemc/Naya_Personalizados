from django.shortcuts import render

def index(request):
    context = {
        'site_title': 'Home',
    }

    return render(
        request,
        'naya_site/index.html',
        context
    )