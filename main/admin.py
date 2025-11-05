from django.contrib import admin
from .models import Category,Product,ProductImage, Size, ProductSize

class ProductImageInLine(admin.TabularInline):
    model = ProductImage
    extra = 1

class ProductSizeInline(admin.TabularInline):
    model = ProductSize
    extra = 1

class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'color' , 'price', 'feed']
    list_filter = ['category', 'color']
    search_fields = ['name', 'color' , 'description']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductImageInLine,ProductSizeInline]

class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'feed']
    prepopulated_fields = {'slug': ('name',)}

class SizeAdmin(admin.ModelAdmin):
    list_display = ['name']

admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Size, SizeAdmin)