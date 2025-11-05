from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model, authenticate
from django.utils.html import strip_tags
from django.core.validators import RegexValidator


User = get_user_model()


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, max_length=254, widget=forms.EmailInput(attrs={'class': 'dotted-input w-full py-3 text-sm font-medium text-gray-900 placeholder-gray-500', 'placeholder': 'EMAIL'}))
    login = forms.CharField(required=True, max_length=50, widget=forms.TextInput(attrs={'class': 'dotted-input w-full py-3 text-sm font-medium text-gray-900 placeholder-gray-500', 'placeholder': 'LOGIN'}))
    first_name = forms.CharField(required=True, max_length=50, widget=forms.TextInput(attrs={'class': 'dotted-input w-full py-3 text-sm font-medium text-gray-900 placeholder-gray-500', 'placeholder': 'FIRST NAME'}))
    last_name = forms.CharField(required=True, max_length=50, widget=forms.TextInput(attrs={'class': 'dotted-input w-full py-3 text-sm font-medium text-gray-900 placeholder-gray-500', 'placeholder': 'LAST NAME'}))
    password1 = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={'class': 'dotted-input w-full py-3 text-sm font-medium text-gray-900 placeholder-gray-500', 'placeholder': 'PASSWORD'})
    )
    password2 = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={'class': 'dotted-input w-full py-3 text-sm font-medium text-gray-900 placeholder-gray-500', 'placeholder': 'CONFIRM PASSWORD'})
    )

    class Meta:
        model = User
        fields = ('login', 'first_name', 'last_name', 'email', 'password1', 'password2')  # Добавлен login

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('This email is already in use.')
        return email

    def clean_login(self):
        login = self.cleaned_data.get('login')
        if User.objects.filter(login=login).exists():
            raise forms.ValidationError('This login is already in use.')
        return login


class CustomUserLoginForm(AuthenticationForm):
    username = forms.CharField(label="Email", widget=forms.TextInput(attrs={'class': 'dotted-input w-full py-3 text-sm font-medium text-gray-900 placeholder-gray-500', 'placeholder': 'EMAIL'}))
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={'class': 'dotted-input w-full py-3 text-sm font-medium text-gray-900 placeholder-gray-500', 'placeholder': 'PASSWORD'})
    )

    def clean(self):
        email = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if email and password:
            self.user_cache = authenticate(self.request, username=email, password=password)  # Исправлено: username=email
            if self.user_cache is None:
                raise forms.ValidationError('Invalid email or password.')
            elif not self.user_cache.is_active:  # Исправлено: убрал скобки
                raise forms.ValidationError('This account is inactive.')
        return self.cleaned_data


class CustomUserUpdateForm(forms.ModelForm):
    login = forms.CharField(
        required=True,
        max_length=50,
        widget=forms.TextInput(attrs={'class': 'dotted-input w-full py-3 text-sm font-medium text-gray-900 placeholder-gray-500', 'placeholder': 'LOGIN'})
    )
    first_name = forms.CharField(
        required=True,
        max_length=50,
        widget=forms.TextInput(attrs={'class': 'dotted-input w-full py-3 text-sm font-medium text-gray-900 placeholder-gray-500', 'placeholder': 'FIRST NAME'})
    )
    last_name = forms.CharField(
        required=True,
        max_length=50,
        widget=forms.TextInput(attrs={'class': 'dotted-input w-full py-3 text-sm font-medium text-gray-900 placeholder-gray-500', 'placeholder': 'LAST NAME'})
    )
    email = forms.EmailField(
        required=True, 
        widget=forms.EmailInput(attrs={'class': 'dotted-input w-full py-3 text-sm font-medium text-gray-900 placeholder-gray-500', 'placeholder': 'EMAIL'})
    )

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email=email).exclude(id=self.instance.id).exists():
            raise forms.ValidationError('This email is already in use.')
        return email

    def clean_login(self):
        login = self.cleaned_data.get('login')
        if login and User.objects.filter(login=login).exclude(id=self.instance.id).exists():
            raise forms.ValidationError('This login is already in use.')
        return login
    

from django import forms
from .models import Product, ProductImage, Category

class AddProductForm(forms.ModelForm):
    name = forms.CharField(
        required=True,
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'dotted-input w-full py-3 text-sm font-medium text-gray-900 placeholder-gray-500', 
            'placeholder': 'NAME'
        })
    )
    color = forms.CharField(
        required=True,
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'dotted-input w-full py-3 text-sm font-medium text-gray-900 placeholder-gray-500', 
            'placeholder': 'COLOR'
        })
    )
    price = forms.DecimalField(
        required=True, 
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'dotted-input w-full py-3 text-sm font-medium text-gray-900 placeholder-gray-500', 
            'placeholder': 'PRICE'
        })
    )
    description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'dotted-input w-full py-3 text-sm font-medium text-gray-900 placeholder-gray-500', 
            'placeholder': 'DESCRIPTION',
            'rows': 4
        })
    )
    main_image = forms.ImageField(
        required=True,
        widget=forms.FileInput(attrs={
            'class': 'dotted-input w-full py-3 text-sm font-medium text-gray-900 placeholder-gray-500'
        })
    )
    extra_image = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'dotted-input w-full py-3 text-sm font-medium text-gray-900 placeholder-gray-500'
        })
    )

    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=True,
        empty_label="Select Category",
        widget=forms.Select(attrs={
            'class': 'dotted-input w-full py-3 text-sm font-medium text-gray-900'
        })
    )

    class Meta:
        model = Product
        fields = ('name','color', 'price', 'description', 'main_image', 'category')