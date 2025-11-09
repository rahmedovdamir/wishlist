from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Profile routes
    path('profile/', views.profile_view, name='profile'),  
    path('edit-account-details/', views.edit_account_details, name='edit_account_details'),
    path('update-account-details/', views.update_account_details, name='update_account_details'),
    
    # Product routes
    path('create_product/', views.create_product, name='create_product'),  
    path('delete/<int:product_id>/', views.DeleteUserProduct, name='delete_product'),
    
    # Password reset routes
    path('password-reset/', views.password_reset_request, name='password_reset_request'),
    path('password-reset/<uidb64>/<token>/', views.password_reset_confirm, name='password_reset_confirm'),
    
    # Dynamic user routes - ДОЛЖНЫ БЫТЬ ПОСЛЕДНИМИ
    path('<str:login>/add/<int:product_id>/', views.add_product, name='add_product'),
    path('<str:login>/', views.ProfileProductsView.as_view(), name='profile_products_view'),
]