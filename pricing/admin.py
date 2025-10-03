from django.contrib import admin
from .models import Category, PriceType, Price, PriceHistory

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'is_active', 'created_at', 'updated_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['name']

@admin.register(PriceType)
class PriceTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'action', 'base_currency', 'target_currency', 'is_active', 'created_at']
    list_filter = ['category', 'action', 'is_active', 'created_at']
    search_fields = ['name', 'base_currency', 'target_currency']
    ordering = ['category__name', 'action', 'name']

@admin.register(Price)
class PriceAdmin(admin.ModelAdmin):
    list_display = ['price_type', 'price', 'created_at', 'updated_at']
    list_filter = ['price_type__category', 'price_type__action', 'created_at']
    search_fields = ['price_type__name']
    ordering = ['-created_at']

@admin.register(PriceHistory)
class PriceHistoryAdmin(admin.ModelAdmin):
    list_display = ['price_type', 'old_price', 'new_price', 'change_percentage', 'changed_at']
    list_filter = ['price_type__category', 'price_type__action', 'changed_at']
    search_fields = ['price_type__name', 'notes']
    ordering = ['-changed_at']
    readonly_fields = ['change_percentage']
