from django.shortcuts import render, redirect,get_object_or_404
from store.models import Product
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
    
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
    except Cart.DoesNotExist:
        cart = Cart.objects.create(cart_id=_cart_id(request))
    cart.save()

    try:
        cart_item = CartItem.objects.get(product=product, cart=cart)
        cart_item.quantity += 1
        cart_item.save()
    except CartItem.DoesNotExist:
        cart_item = CartItem.objects.create(
            product = product,
            quantity = 1,
            cart = cart,
        )
        cart_item.save()

    return redirect('cart')

# ৩. কার্ট পেজ এবং মোট দাম দেখানোর ফাংশন
def cart(request):
    total = 0
    cart_items = None
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
    except ObjectDoesNotExist:
        pass 

    context = {
        'total': total,
        'cart_items': cart_items,
    }
    return render(request,'cart.html', context)

# ... (আপনার আগের _cart_id, add_cart এবং cart ফাংশনগুলো এখানে ঠিক তেমনই থাকবে) ...

# কার্ট থেকে প্রোডাক্টের পরিমাণ কমানো (-)
def remove_cart(request, product_id):
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product, id=product_id)
    try:
        cart_item = CartItem.objects.get(product=product, cart=cart)
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete() # পরিমাণ ১ এর কম হলে প্রোডাক্ট ডিলিট হয়ে যাবে
    except:
        pass
    return redirect('cart')

# কার্ট থেকে প্রোডাক্ট একদম মুছে ফেলা (Remove)
def remove_cart_item(request, product_id):
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product, id=product_id)
    cart_item = CartItem.objects.get(product=product, cart=cart)
    cart_item.delete()
    return redirect('cart')

def checkout(request):
    total = 0
    cart_items = None
    try:
        # কার্ট এবং আইটেম খুঁজে বের করা
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
    except ObjectDoesNotExist:
        pass 

    context = {
        'total': total,
        'cart_items': cart_items,
    }
    return render(request,'checkout.html', context)