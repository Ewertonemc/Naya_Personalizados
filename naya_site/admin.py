from django.contrib import admin
from naya_site import models
from .models import Category, Product, Orcamento, ItemOrcamento, ArquivoOrcamento


@admin.register(models.Product)
class productAdmin(admin.ModelAdmin):
    list_display = ('id', 'image', 'name', 'quantity',
                    'unit_value', 'total_value', 'category',)
    ordering = ('-name',)
    # list_filter = ('created_date',)
    search_fields = ('id', 'name', 'category',)
    list_per_page = 10
    list_max_show_all = 50
    # list_editable = ('name',)
    list_display_links = ('name',)


@admin.register(models.Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = 'name',
    ordering = ('-id',)


@admin.register(models.State)
class StateAdmin(admin.ModelAdmin):
    list_display = 'name',
    ordering = ('-id',)


@admin.register(models.UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'cpf', 'state', 'cidade', 'logradouro',
                    'cep', 'numero', 'complemento', 'bairro',)
    ordering = ('-id',)
    search_fields = ('user__username', 'cpf', 'cidade', 'state',)
    list_per_page = 10
    list_max_show_all = 50
    list_display_links = ('user',)


class ItemOrcamentoInline(admin.TabularInline):
    model = ItemOrcamento
    extra = 0


@admin.register(Orcamento)
class OrcamentoAdmin(admin.ModelAdmin):
    list_display = ['id', 'cliente', 'data_criacao', 'status', 'valor_total']
    list_filter = ['status', 'data_criacao']
    search_fields = ['cliente__username',
                     'cliente__first_name', 'cliente__last_name']
    inlines = [ItemOrcamentoInline]
    readonly_fields = ['id', 'data_criacao']


@admin.register(ArquivoOrcamento)
class ArquivoOrcamentoAdmin(admin.ModelAdmin):
    list_display = ['nome_original', 'tipo', 'data_upload']
    list_filter = ['tipo', 'data_upload']
