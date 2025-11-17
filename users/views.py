from venv import logger
from django.shortcuts import render, redirect , get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.http import HttpResponse, JsonResponse
from django.template.response import TemplateResponse
from .forms import CustomUserCreationForm, CustomUserLoginForm, CustomUserUpdateForm , AddProductForm, PasswordResetRequestForm, PasswordResetConfirmForm
from .tasks import send_welcome_email, send_password_reset_email
from .models import CustomUser
from django.contrib import messages
from main.models import Product, Category
from django.views.generic import TemplateView, DetailView
from django.contrib.auth import update_session_auth_hash
from slugify import slugify
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import  urlsafe_base64_decode
from django.utils.encoding import force_str
import logging



def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            send_welcome_email.delay(user.email, user.first_name)
            logger.info(f"Welcome email task queued for {user.email}")
            if request.headers.get('HX-Request'):
                response = HttpResponse()
                response['HX-Redirect'] = reverse('main:index')
                return response
            return redirect('main:index')
        else:
            if request.headers.get('HX-Request'):
                return render(request, 'users/register_content.html', {'form': form})
    else:
        form = CustomUserCreationForm()
        if request.headers.get('HX-Request'):
            return render(request, 'users/register_content.html', {'form': form})
    return render(request, 'users/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = CustomUserLoginForm(request=request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            if request.headers.get('HX-Request'):
                response = HttpResponse()
                response['HX-Redirect'] = reverse('main:index')
                return response
            return redirect('main:index')
        else:
            if request.headers.get('HX-Request'):
                return render(request, 'users/login_content.html', {'form': form})  
    else:
        form = CustomUserLoginForm()
        if request.headers.get('HX-Request'):
            return render(request, 'users/login_content.html', {'form': form})  
    return render(request, 'users/login.html', {'form': form})

@login_required(login_url='/users/login')
def profile_view(request):
    template_name = 'users/profile.html'
    if request.method == 'POST':
        form = CustomUserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            if request.headers.get("HX-Request"):
                return HttpResponse(headers={'HX-Redirect': reverse('users:profile')})
            return redirect('users:profile')
    else:
        form = CustomUserUpdateForm(instance=request.user)

    if request.headers.get("HX-Request"):
        return TemplateResponse(request, 'users/profile_content.html', {
        'form': form,
        'user': request.user
    })
    return TemplateResponse(request, template_name, {
        'form': form,
        'user': request.user
    })

@login_required(login_url='/users/login')
def edit_account_details(request):
    form = CustomUserUpdateForm(instance=request.user)
    return TemplateResponse(request, 'users/partials/edit_account_details.html',
                            {'user': request.user, 'form': form})

@login_required(login_url='/users/login')
def update_account_details(request):
    if request.method == 'POST':
        form = CustomUserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            user = form.save(commit=False)
            user.clean()
            user.save()
            if request.headers.get('HX-Request'):
                response = HttpResponse()
                response['HX-Redirect'] = reverse('users:profile')
                return response
            else:
                return redirect('users:profile')
        else:
            return TemplateResponse(request, 'users/partials/edit_account_details.html', 
                                  {'user': request.user, 'form': form})
    
    if request.headers.get('HX-Request'):
        response = HttpResponse()
        response['HX-Redirect'] = reverse('users:profile')
        return response
    return redirect('users:profile')

def logout_view(request):
    logout(request)
    if request.headers.get('HX-Request'):
        return redirect('main:index')
    return redirect('main:index')


class ProfileProductsView(TemplateView):
    template_name = 'main/product_view.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        login = kwargs.get('login')

        try:
            user = CustomUser.objects.get(login=login)
            products_ids = user.get_product_ids()
        except CustomUser.DoesNotExist:
            products_ids = []
        
        context["login"] = login
        context["access"] =user.access
        context["products_list_ids"] = products_ids
        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        if request.headers.get("HX-Request"):
            return TemplateResponse(request, "users/product_view_content.html", context)
        return TemplateResponse(request, "users/product_view.html", context)


def DeleteUserProduct(request, *args, **kwargs):
    product_id = kwargs.get('product_id')
    
    try:
        user = request.user
        login = user.login
        if request.user.login != login:
            if request.headers.get('HX-Request'):
                return HttpResponse(
                    '<button class="w-full  py-3 px-6 text-sm font-medium bg-black text-white cursor-not-allowed" disabled>ACCESS DENIED</button>'
                )
            return redirect('users:profile_products_view', login=request.user.login)
    
        product = user.products.get(id=product_id)
            
        if product:
            user.products.remove(product)
            if request.headers.get('HX-Request'):
                    return HttpResponse(
                        '<button class="w-full  py-3 px-6 text-sm font-medium bg-black text-white cursor-not-allowed" disabled>DELETED</button>'
                    )
        else:
            return HttpResponse(
                '<button class="w-full  py-3 px-6 text-sm font-medium bg-black text-white cursor-not-allowed" disabled>Product doesnt exists</button>'
            )
        
    except Exception as e:
        print(f"Error adding product: {e}")
        if request.headers.get('HX-Request'):
            return HttpResponse(
                '<button class="w-full  py-3 px-6 text-sm font-medium bg-black text-white cursor-not-allowed" disabled>ERROR</button>'
            )
    return redirect('users:profile_products_view', login=login)


@login_required
def add_product(request, *args, **kwargs):
    product_id = kwargs.get('product_id')
    login = kwargs.get('login')
    
    if request.user.login != login:
        if request.headers.get('HX-Request'):
            return HttpResponse(
                '<button class="w-full  py-3 px-6 text-sm font-medium bg-black text-white cursor-not-allowed" disabled>ACCESS DENIED</button>'
            )
        return redirect('users:profile_products_view', login=request.user.login)
    
    try:
        user = get_object_or_404(CustomUser, login=login)
        product = get_object_or_404(Product, id=product_id)
        
        if user.products.filter(id=product_id).exists():
            if request.headers.get('HX-Request'):
                return HttpResponse (
                    '<button class="w-full  py-3 px-6 text-sm font-medium bg-black text-white cursor-not-allowed" disabled>ALREADY IN WISHLIST</button>'
                )
        else:
            user.products.add(product)
            if request.headers.get('HX-Request'):
                return HttpResponse(
                    '<button class="w-full  py-3 px-6 text-sm font-medium bg-black text-white cursor-not-allowed" disabled>ADDED TO WISHLIST</button>'
                )
            
    except Exception as e:
        print(f"Error adding product: {e}")
        if request.headers.get('HX-Request'):
            return HttpResponse(
                '<button class="w-full  py-3 px-6 text-sm font-medium bg-black text-white cursor-not-allowed" disabled>ERROR</button>'
            )

    
    return redirect('users:profile_products_view', login=login)


@login_required
def create_product(request):
    if request.method == 'POST':
        form = AddProductForm(request.POST, request.FILES)
        if form.is_valid():
            category_name = form.cleaned_data['category']
            category,created = Category.objects.get_or_create(
                name=category_name,
                defaults={'slug': slugify(category_name)} 
            )
            product = form.save(commit=False)
            product.category = category
            product.save()
            request.user.products.add(product)
            if request.headers.get('HX-Request'):
                response = HttpResponse()
                response['HX-Redirect'] = reverse('users:profile_products_view', kwargs={'login': request.user.login})
                return response
            else:
                return redirect('users:profile_products_view', login=request.user.login)
        else:
            return TemplateResponse(request, 'users/create_product_content.html', {'form': form})
    
    else:
        form = AddProductForm()
        if request.headers.get('HX-Request'):
            return TemplateResponse(request, 'users/create_product_content.html', {'form': form})
        else:
            return TemplateResponse(request, 'users/create_product.html', {'form': form})

def password_reset_request(request):
    if request.method == 'POST':
        form = PasswordResetRequestForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            user = CustomUser.objects.filter(email=email).first()
            if user:
                logger.info(f"Attempting to send password reset email to {email} for user ID {user.pk}")
                send_password_reset_email.delay(email, user.pk)
                messages.success(request, "Password reset email has been queued. Please check your inbox or spam folder.")
                return render(request, 'users/password_reset_done.html')
            else:
                messages.warning(request, "No account found with this email.")
        else:
            messages.error(request, "Please enter a valid email address.")
    else:
        form = PasswordResetRequestForm()
    return render(request, 'users/password_reset_request.html', {'form': form})


def password_reset_confirm(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = CustomUser.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            form = PasswordResetConfirmForm(request.POST)
            if form.is_valid():
                user.set_password(form.cleaned_data['new_password1'])
                user.save()
                messages.success(request, "Your password has been reset successfully.")
                return render(request, 'users/password_reset_complete.html')
        else:
            form = PasswordResetConfirmForm()
        return render(request, 'users/password_reset_confirm.html', {'form': form, 'validlink': True})
    else:
        return render(request, 'users/password_reset_confirm.html', {'validlink': False})
