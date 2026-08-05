from django.shortcuts import render, get_object_or_404, redirect
from store.models import Product, Category, ProductGallery, Variation
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from store.forms import ProductForm

# Create your views here.

# --- হোমপেজ (সিলেক্ট রিলেটেড দিয়ে অপ্টিমাইজ করা হলো যাতে ডুপ্লিকেট কুয়েরি না হয়) ---
def home(request, category_slug=None):
    categories = None
    products = None

    if category_slug != None:
        categories = get_object_or_404(Category, slug=category_slug)
        # .select_related('category') যুক্ত করা হয়েছে
        products = Product.objects.filter(category=categories, is_available=True).select_related('category').order_by('-id')
    else:
        # .select_related('category') যুক্ত করা হয়েছে
        products = Product.objects.filter(is_available=True).select_related('category').order_by('-id')

    all_categories = Category.objects.all()

    context = {
        'products': products,
        'all_categories': all_categories,
    }
    return render(request, 'home.html', context)

def search(request):
    products = None
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        if keyword:
            products = Product.objects.filter(Q(description__icontains=keyword) | Q(product_name__icontains=keyword)).select_related('category')
    
    context = {
        'products': products,
    }
    return render(request, 'home.html', context)

def product_detail(request, category_slug, product_slug):
    try:
        # select_related দিয়ে ক্যাটাগরি এবং prefetch_related দিয়ে গ্যালারি ও ভেরিয়েশন একসাথে নিয়ে আসা হচ্ছে
        single_product = Product.objects.select_related('category').prefetch_related(
            'productgallery_set', 
            'variation_set'
        ).get(category__slug=category_slug, slug=product_slug)
    except Exception as e:
        raise e
        
    # যেহেতু prefetch_related ব্যবহার করা হয়েছে, তাই পাইথনের মেমোরি থেকেই এগুলো ফিল্টার হয়ে যাবে (নতুন করে ডাটাবেজে হিট করবে না)
    colors = [v for v in single_product.variation_set.all() if v.variation_category == 'color' and v.is_active]
    sizes = [v for v in single_product.variation_set.all() if v.variation_category == 'size' and v.is_active]
    
    product_gallery = single_product.productgallery_set.all()
    
    related_products = Product.objects.filter(
        category=single_product.category, 
        is_available=True
    ).select_related('category').exclude(id=single_product.id)[:4]
    
    context = {
        'single_product': single_product,
        'product_gallery': product_gallery, 
        'colors': colors,
        'sizes': sizes,
        'related_products': related_products,
    }
    return render(request, 'product_detail.html', context)

@login_required(login_url='/admin/login/')
def add_product(request):
    if not request.user.is_superuser:
        return redirect('home')

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES) 
        if form.is_valid():
            product = form.save()
            
            colors_str = form.cleaned_data.get('colors')
            if colors_str:
                color_list = [c.strip() for c in colors_str.split(',')]
                for color in color_list:
                    if color:
                        Variation.objects.create(product=product, variation_category='color', variation_value=color)
            
            sizes_str = form.cleaned_data.get('sizes')
            if sizes_str:
                size_list = [s.strip() for s in sizes_str.split(',')]
                for size in size_list:
                    if size:
                        Variation.objects.create(product=product, variation_category='size', variation_value=size)

            images = request.FILES.getlist('gallery_images') 
            for img in images:
                ProductGallery.objects.create(product=product, image=img)

            return redirect('home')
    else:
        form = ProductForm()

    return render(request, 'add_product.html', {'form': form})

@login_required(login_url='/admin/login/')
def manage_products(request):
    if not request.user.is_superuser:
        return redirect('home')
    products = Product.objects.all().select_related('category').order_by('-id')
    return render(request, 'manage_products.html', {'products': products})

@login_required(login_url='/admin/login/')
def edit_product(request, product_id):
    if not request.user.is_superuser:
        return redirect('home')
    
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect('manage_products')
    else:
        form = ProductForm(instance=product)
    
    return render(request, 'add_product.html', {'form': form, 'edit_mode': True})

@login_required(login_url='/admin/login/')
def delete_product(request, product_id):
    if not request.user.is_superuser:
        return redirect('home')
    
    product = get_object_or_404(Product, id=product_id)
    product.delete()
    return redirect('manage_products')