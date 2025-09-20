from django.urls import path
from naya_site import views

app_name = 'naya_site'

urlpatterns = [
    path('', views.index, name='index'),
]