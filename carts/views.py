from django.shortcuts import render, redirect, get_object_or_404
from store.models import Product, Variation
from store.models import Cart, CartItem
from django.core.exceptions import ObjectDoesNotExist

# ১. ইউজারের ব্রাউজার সেশন আইডি বের করার ফাংশন
def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart

# ২. কার্টে প্রোডাক্ট যুক্ত করার ফাংশন (Add to Cart)
def add_cart(request, product_id):
    product = Product.objects.get(id=product_id)
    product_variation = []

    # ফর্ম থেকে সাইজ এবং কালার রিসিভ করা
    if request.method == 'POST':
        for item in request.POST:
            key = item
            value = request.POST[key]
            try:
                variation = Variation.objects.get(product=product, variation_category__iexact=key, variation_value__iexact=value)
                product_variation.append(variation)
            except:
                pass

    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
    except Cart.DoesNotExist:
        cart = Cart.objects.create(cart_id=_cart_id(request))
    cart.save()

    is_cart_item_exists = CartItem.objects.filter(product=product, cart=cart).exists()

    if is_cart_item_exists:
        cart_item = CartItem.objects.filter(product=product, cart=cart)
        ex_var_list = []
        id = []
        for item in cart_item:
            existing_variation = item.variations.all()
            ex_var_list.append(list(existing_variation))
            id.append(item.id)

        if product_variation in ex_var_list:
            index = ex_var_list.index(product_variation)
            item_id = id[index]
            item = CartItem.objects.get(product=product, id=item_id)
            item.quantity += 1
            item.save()
        else:
            item = CartItem.objects.create(product=product, quantity=1, cart=cart)
            if len(product_variation) > 0:
                item.variations.clear()
                item.variations.add(*product_variation)
            item.save()
    else:
        cart_item = CartItem.objects.create(product=product, quantity=1, cart=cart)
        if len(product_variation) > 0:
            cart_item.variations.clear()
            cart_item.variations.add(*product_variation)
        cart_item.save()

    return redirect('cart')

# ৩. কার্ট পেজ এবং মোট দাম দেখানোর ফাংশন (অপ্টিমাইজড)
def cart(request):
    total = 0
    cart_items = None
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        # select_related এবং prefetch_related যুক্ত করা হয়েছে যাতে ডুপ্লিকেট কুয়েরি না হয়
        cart_items = CartItem.objects.filter(cart=cart, is_active=True).select_related('product').prefetch_related('variations')
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
    except ObjectDoesNotExist:
        pass 
    context = {
        'total': total,
        'cart_items': cart_items,
    }
    return render(request, 'cart.html', context)

# ৪. কার্ট থেকে প্রোডাক্টের পরিমাণ কমানো (-)
def remove_cart(request, product_id, cart_item_id):
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product, id=product_id)
    try:
        cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete() 
    except:
        pass
    return redirect('cart')

# ৫. কার্ট থেকে প্রোডাক্ট একদম মুছে ফেলা (Remove)
def remove_cart_item(request, product_id, cart_item_id):
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product, id=product_id)
    cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)
    cart_item.delete()
    return redirect('cart')

# ৬. চেকআউট পেজের ফাংশন (অপ্টিমাইজড)
def checkout(request):
    total = 0
    cart_items = None
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        # select_related এবং prefetch_related যুক্ত করা হয়েছে
        cart_items = CartItem.objects.filter(cart=cart, is_active=True).select_related('product').prefetch_related('variations')
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
    except ObjectDoesNotExist:
        pass 
    context = {
        'total': total,
        'cart_items': cart_items,
    }
    return render(request, 'checkout.html', context)

# ৭. কার্টে প্রোডাক্টের পরিমাণ বাড়ানো (+)
def increase_cart_item(request, product_id, cart_item_id):
    try:
        cart_item = CartItem.objects.get(product_id=product_id, id=cart_item_id)
        cart_item.quantity += 1
        cart_item.save()
    except CartItem.DoesNotExist:
        pass
    return redirect('cart')