from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'login', 'first_name', 'last_name', 'is_staff', 'access')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups' , 'access')
    search_fields = ('email', 'login', 'first_name', 'last_name', 'access')
    ordering = ('email',)
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {
            'fields': ('login', 'first_name', 'last_name', 'products', 'access')
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser',
                       'groups', 'user_permissions')
        }),
        ('Important dates', {
            'fields': ('last_login', 'date_joined')
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'login', 'first_name', 'last_name', 'password1',
                       'password2', 'is_staff', 'is_active'),
        }),
    )
    
    # Добавляем фильтр горизонтальный для товаров
    filter_horizontal = ('products', 'groups', 'user_permissions')

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if 'username' in form.base_fields:
            form.base_fields['username'].disabled = True
        return form


admin.site.register(CustomUser, CustomUserAdmin)