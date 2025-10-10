from django.urls import path
from naya_site import views

app_name = 'naya_site'

urlpatterns = [
    path('', views.index, name='index'),
    path('product/search/', views.search, name='search'),


    path('estoque/', views.stock, name='stock'),
    path('product/<int:product_id>/', views.product, name='product'),
    path('product/create/', views.create, name='create'),
    path('product/<int:product_id>/update/', views.update, name='update'),
    path('product/<int:product_id>/delete/', views.delete, name='delete'),


    path('user/create/', views.register, name='register'),
    path('user/login/', views.login_view, name='login'),
    path('user/logout/', views.logout_view, name='logout'),
    path('user/perfil/', views.perfil, name='perfil'),
    path('user/update/', views.user_update, name='user_update'),

    # Cliente
    path('dashboard', views.dashboard_orcamentos, name='dashboard'),
    path('orçamento/', views.criar_orcamento, name='criar_orcamento'),
    path('detalhe/<uuid:orcamento_id>/',
         views.detalhe_orcamento, name='detalhe_orcamento'),
    path('responder/<uuid:orcamento_id>/',
         views.responder_orcamento, name='responder_orcamento'),

    # API
    path('api/produto/<int:produto_id>/',
         views.get_produto_info, name='produto_info'),

    # Administração
    path('naya/', views.admin_dashboard, name='admin_dashboard'),
    path('naya/responder/<uuid:orcamento_id>/',
         views.admin_responder_orcamento, name='admin_responder'),
]
