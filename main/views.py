from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView, DetailView
from django.http import HttpResponse
from django.template.response import TemplateResponse
from .models import Category, Product, Size
from django.db.models import Q

class IndexView(TemplateView):
    template_name = 'main/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['current_category'] = None
        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        if request.headers.get("HX-Request"):
            return TemplateResponse(request, 'main/home_content.html', context)
        return TemplateResponse(request, self.template_name, context)
    
class CatalogView(TemplateView):
    template_name = 'main/catalog.html'

    FILTER_MAPPING = {
        'color': lambda queryset, value: queryset.filter(color__iexact=value),
        'min_price': lambda queryset, value: queryset.filter(price__gte=float(value)),
        'max_price': lambda queryset, value: queryset.filter(price__lte=float(value)),  
        'size': lambda queryset, value: queryset.filter(productsizes__sizes__name=value).distinct()  
    }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category_slug = kwargs.get('category_slug')
        categories = Category.objects.all()
        products = Product.objects.all().order_by('-created_at') 
        current_category = None
        if category_slug:
            current_category = get_object_or_404(Category, slug=category_slug)
            products = products.filter(category=current_category)
        
        query = self.request.GET.get('q')
        if query:
            products = products.filter(
                Q(name__icontains=query) | Q(description__icontains=query)
            )
        
        filter_params = {}
        for param, filter_func in self.FILTER_MAPPING.items():
            value = self.request.GET.get(param)
            if value:
                try:
                    products = filter_func(products, value)
                    filter_params[param] = value
                except (ValueError, TypeError):
                    
                    continue
        
        filter_params['q'] = query or ''

        context.update({
            'categories': categories,
            'products': products,
            'current_category': current_category,  
            'filter_params': filter_params,
            'sizes': Size.objects.all(),
            'search_query': query or '',
            'show_search': self.request.GET.get('show_search') == 'true',
            'reset_search': self.request.GET.get('reset_search') == 'true'
        })
        
        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        if request.headers.get("HX-Request"):
            if context.get('show_search'):
                return TemplateResponse(request, "main/search_input.html", context)
            elif context.get('reset_search'):
                return TemplateResponse(request, "main/search_button.html", context)  
            template = "main/filter_modal.html" if request.GET.get('show_filters') == 'true' else 'main/catalog_content.html'
            return TemplateResponse(request, template, context)
        return TemplateResponse(request, self.template_name, context)
    
class ProductDetailView(DetailView):
    model = Product
    template_name = 'main/product_detail.html'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.get_object()
        context['categories'] = Category.objects.all()
        if self.request.user.is_authenticated:
            context['user_login'] = self.request.user.login
        else:
            context['user_login'] = None
        if product.category:
            context['current_category'] = product.category.slug
        else:
            context['current_category'] = 'some-category-slug'
        return context
    

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data(**kwargs)
        if request.headers.get('HX-Request'):
            return TemplateResponse(request, 'main/product_detail_content.html', context)
        return TemplateResponse(request, self.template_name, context)