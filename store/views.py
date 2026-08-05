from django.shortcuts import render, get_object_or_404, redirect
from store.models import Product, Category, ProductGallery, Variation
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from store.forms import ProductForm

# Create your views here.

# --- হোমপেজ (যেখানেই সব প্রোডাক্ট এবং ক্যাটাগরি ফিল্টার থাকবে) ---
def home(request, category_slug=None):
    categories = None
    products = None

    # যদি ইউজার ওপরের মেনু থেকে কোনো ক্যাটাগরিতে ক্লিক করে
    if category_slug != None:
        categories = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(category=categories, is_available=True).order_by('-id')
    # যদি একদম হোমপেজে থাকে (All Products)
    else:
        products = Product.objects.filter(is_available=True).order_by('-id')

    # মেনুবারে দেখানোর জন্য সব ক্যাটাগরি
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
            # প্রোডাক্টের নাম অথবা ডেসক্রিপশনের মধ্যে কিওয়ার্ডটি খুঁজবে
            products = Product.objects.filter(Q(description__icontains=keyword) | Q(product_name__icontains=keyword))
    
    context = {
        'products': products,
    }
    return render(request, 'home.html', context)

def product_detail(request, category_slug, product_slug):
    try:
        single_product = Product.objects.get(category__slug=category_slug, slug=product_slug)
    except Exception as e:
        raise e
        
    # এই প্রোডাক্টের সব ছবি নিয়ে আসা
    product_gallery = ProductGallery.objects.filter(product_id=single_product.id)
    
    # --- নতুন ফিচার: একই ক্যাটাগরির অন্য প্রোডাক্ট নিয়ে আসা (Related Products) ---
    # বর্তমান প্রোডাক্টের ক্যাটাগরি দিয়ে ফিল্টার করা হয়েছে এবং exclude দিয়ে বর্তমান প্রোডাক্টটি বাদ দেওয়া হয়েছে
    # [:4] দিয়ে বলা হয়েছে যে নিচে শুধুমাত্র ৪টি প্রোডাক্ট দেখাবে
    related_products = Product.objects.filter(
        category=single_product.category, 
        is_available=True
    ).exclude(id=single_product.id)[:4]
    
    context = {
        'single_product': single_product,
        'product_gallery': product_gallery, 
        'related_products': related_products, # টেমপ্লেটে পাঠানোর জন্য অ্যাড করা হলো
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
    products = Product.objects.all().order_by('-id')
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