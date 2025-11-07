from django.contrib import admin
from naya_site import models
from .models import Category, Product, Orcamento, ItemOrcamento, ArquivoOrcamento, CategoriaGaleria, ImagemGaleria, State, UserProfile
from django.utils.html import format_html


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


class FiltroAtivo(admin.SimpleListFilter):
    title = 'status'
    parameter_name = 'ativa'

    def lookups(self, request, model_admin):
        return (
            ('1', 'Ativas'),
            ('0', 'Inativas'),
        )

    def queryset(self, request, queryset):
        if self.value() == '1':
            return queryset.filter(ativa=True)
        if self.value() == '0':
            return queryset.filter(ativa=False)


class ImagemGaleriaInline(admin.TabularInline):
    model = ImagemGaleria
    extra = 1
    fields = ['imagem', 'preview_imagem', 'descricao', 'ativa', 'ordem']
    readonly_fields = ['preview_imagem']

    def preview_imagem(self, obj):
        if obj.imagem and hasattr(obj.imagem, 'url'):
            return format_html('<img src="{}" style="max-height: 50px; max-width: 50px; border-radius: 4px;" />', obj.imagem.url)
        return "-"
    preview_imagem.short_description = "Preview"


@admin.register(CategoriaGaleria)
class CategoriaGaleriaAdmin(admin.ModelAdmin):
    list_display = ['nome', 'slug', 'ativa', 'ordem', 'quantidade_imagens']
    list_editable = ['ativa', 'ordem']
    list_filter = ['ativa']
    search_fields = ['nome']
    prepopulated_fields = {'slug': ('nome',)}
    inlines = [ImagemGaleriaInline]

    def quantidade_imagens(self, obj):
        return obj.imagemgaleria_set.count()
    quantidade_imagens.short_description = "Qtd. Imagens"


@admin.register(ImagemGaleria)
class ImagemGaleriaAdmin(admin.ModelAdmin):
    list_display = ['preview_imagem', 'descricao',
                    'categoria', 'ativa', 'ordem', 'data_upload_formatado']
    list_editable = ['descricao', 'categoria', 'ativa', 'ordem']
    list_filter = [FiltroAtivo, 'categoria', 'data_upload']
    search_fields = ['descricao', 'categoria__nome']
    list_per_page = 25
    date_hierarchy = 'data_upload'

    def preview_imagem(self, obj):
        if obj.imagem and hasattr(obj.imagem, 'url'):
            return format_html('<img src="{}" style="max-height: 50px; max-width: 50px; border-radius: 4px;" />', obj.imagem.url)
        return "-"
    preview_imagem.short_description = "Imagem"

    def data_upload_formatado(self, obj):
        return obj.data_upload.strftime("%d/%m/%Y %H:%M")
    data_upload_formatado.short_description = "Data de Upload"
    data_upload_formatado.admin_order_field = 'data_upload'

    # Actions personalizadas
    actions = ['ativar_imagens', 'desativar_imagens', 'mover_para_categoria']

    def ativar_imagens(self, request, queryset):
        updated = queryset.update(ativa=True)
        self.message_user(request, f'{updated} imagens ativadas com sucesso.')
    ativar_imagens.short_description = "Ativar imagens selecionadas"

    def desativar_imagens(self, request, queryset):
        updated = queryset.update(ativa=False)
        self.message_user(
            request, f'{updated} imagens desativadas com sucesso.')
    desativar_imagens.short_description = "Desativar imagens selecionadas"

    def mover_para_categoria(self, request, queryset):
        # Esta action pode ser implementada com um form personalizado
        # Por enquanto, vamos apenas mostrar uma mensagem
        self.message_user(
            request, f'Selecione as imagens e edite a categoria individualmente.')
    mover_para_categoria.short_description = "Mover para outra categoria"
