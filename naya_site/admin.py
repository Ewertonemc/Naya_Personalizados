from django.contrib import admin
from naya_site import models


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
