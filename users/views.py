from django.shortcuts import render, redirect , get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.http import HttpResponse, JsonResponse
from django.template.response import TemplateResponse
from .forms import CustomUserCreationForm, CustomUserLoginForm, CustomUserUpdateForm , AddProductForm
from .models import CustomUser
from django.contrib import messages
from main.models import Product
from django.views.generic import TemplateView, DetailView
from django.contrib.auth import update_session_auth_hash
def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect('main:index')
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = CustomUserLoginForm(request=request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect('main:index')
    else:
        form = CustomUserLoginForm()
    return render(request, 'users/login.html', {'form': form})
    
@login_required(login_url='/users/login')
def profile_view(request):
    if request.method == 'POST':
        form = CustomUserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            if request.headers.get("HX-Request"):
                return HttpResponse(headers={'HX-Redirect': reverse('users:profile')})
            return redirect('users:profile')
    else:
        form = CustomUserUpdateForm(instance=request.user)

    recommended_products = Product.objects.all().order_by('id')[:3]

    return TemplateResponse(request, 'users/profile.html', {
        'form': form,
        'user': request.user,
        'recommended_products': recommended_products
    })


@login_required(login_url='/users/login')
def account_details(request):
    user = CustomUser.objects.get(id=request.user.id)
    return TemplateResponse(request, 'users/partials/account_details.html', {'user': user})


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
            updated_user = CustomUser.objects.get(id=user.id)
            request.user = updated_user
            if request.headers.get('HX-Request'):
                return TemplateResponse(request, 'users/partials/account_details.html', {'user': updated_user})
            return TemplateResponse(request, 'users/partials/account_details.html', {'user': updated_user})
        else:
            return TemplateResponse(request, 'users/partials/edit_account_details.html', {'user': request.user, 'form': form})
    if request.headers.get('HX-Request'):
        return HttpResponse(headers={'HX-Redirect': reverse('user:profile')})
    return redirect('users:profile')

def logout_view(request):
    logout(request)
    if request.headers.get('HX-Request'):
        return redirect('main:index')
    return redirect('main:index')


class ProfileProductsView(TemplateView):
    template_name = 'main/base.html'
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
            product.delete()
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
            product = form.save(commit=False)
            product.save() 
            request.user.products.add(product)
            if request.headers.get('HX-Request'):
                return TemplateResponse(request, 'users/create_product.html', {'form': AddProductForm()}) 
            else:
                return redirect('users:profile_products_view', login = request.user.login)  
        else:
            return TemplateResponse(request, 'users/create_product.html', {'form': form})
    else:
        form = AddProductForm()
        return TemplateResponse(request, 'users/create_product.html', {'form': form})

