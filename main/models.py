from django.db import models
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from slugify import slugify

class Category(models.Model):
    name = models.CharField(max_length=100, null=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    feed = models.BooleanField(default=False)
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name
    
class Size(models.Model):
    name = models.CharField(max_length=20, blank=True, null=True)


    def __str__(self):
        return self.name

class ProductSize(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE,related_name='product_sizes')
    size = models.ForeignKey(Size, on_delete=models.CASCADE)
    stock = models.PositiveIntegerField(default=0)


    def __str__(self):
        return f"{self.size.name} ({self.stock} in stock) for {self.product.name}"


class Product(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    color = models.CharField(max_length=100,null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)
    main_image = models.ImageField(upload_to='products/main/')
    created_at = models.DateTimeField(auto_now_add=True)  
    updated_at = models.DateTimeField(auto_now=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products', null=True, blank=True)
    url = models.URLField(max_length=200, null=True, blank=True)
    feed = models.BooleanField(default=False)

    def clean(self):
        if self.url:
            validator = URLValidator()
            try:
                validator(self.url)
            except ValidationError:
                raise ValidationError("Please enter a valid URL")
            
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)   

    def __str__(self):
        return self.name

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete = models.CASCADE, related_name = 'images')
    image = models.ImageField(upload_to='products/extra/')