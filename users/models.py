from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager

from main.models import Product, ProductImage,Category,ProductSize

class CustomUserManager(BaseUserManager):
    def create_user(self, email, login, first_name, last_name, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set.")
        if not login:
            raise ValueError("The Login field must be set.")
        
        email = self.normalize_email(email)
        user = self.model(
            email=email, 
            login=login, 
            first_name=first_name, 
            last_name=last_name, 
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user 

    def create_superuser(self, email, login, first_name, last_name, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(email, login, first_name, last_name, password, **extra_fields)

class CustomUser(AbstractUser):
    username = None  
    email = models.EmailField(unique=True, max_length=254)
    login = models.CharField(unique=True, max_length=50)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    access = models.BooleanField(default=False)
    products = models.ManyToManyField(Product, related_name='user_products', blank=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['login', 'first_name', 'last_name']

    def get_product_ids(self):
        return list(self.products.all())

    def __str__(self):
        return self.email

