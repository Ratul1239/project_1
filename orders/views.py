from django.shortcuts import render, redirect, get_object_or_404
from store.models import Cart, CartItem, Product
from carts.views import _cart_id
from orders.forms import OrderForm
from orders.models import Order, OrderProduct
from django.contrib.auth.decorators import login_required

def place_order(request):
    cart = Cart.objects.get(cart_id=_cart_id(request))
    cart_items = CartItem.objects.filter(cart=cart, is_active=True)
    cart_count = cart_items.count()
    
    if cart_count <= 0:
        return redirect('home')

    total = 0
    for cart_item in cart_items:
        total += (cart_item.product.price * cart_item.quantity)

    if request.method == 'POST':
        form = OrderForm(request.POST)
        
        if form.is_valid():
            # ১. Order টেবিলে ডেটা সেভ করা
            data = form.save(commit=False)
            data.order_total = total
            data.save() 

            # ২. কার্টের সবগুলো আইটেম OrderProduct টেবিলে সেভ করা
            for item in cart_items:
                order_product = OrderProduct()
                order_product.order_id = data.id
                order_product.product_id = item.product_id
                order_product.quantity = item.quantity
                order_product.product_price = item.product.price
                order_product.save() 

                # --------- ভুল ঠিক করা হয়েছে (Variation এর বদলে variations) ---------
                product_variation = item.variations.all() 
                order_product.variations.set(product_variation) 
                order_product.save()
                # --------------------------------------------------------------------

                # স্টক আপডেট করা
                product = Product.objects.get(id=item.product_id)
                product.stock -= item.quantity 
                product.save()

            # ৩. কার্ট ক্লিয়ার করা
            CartItem.objects.filter(cart=cart).delete()

            # ৪. থ্যাঙ্ক ইউ পেজে পাঠানো
            return redirect('order_complete')
    else:
        return redirect('cart')

def order_complete(request):
    return render(request, 'order_complete.html')

@login_required(login_url='/admin/login/') 
def custom_dashboard(request):
    if not request.user.is_superuser:
        return redirect('home')
    
    orders = Order.objects.all().order_by('-created_at')
    return render(request, 'dashboard.html', {'orders': orders})

def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order_products = OrderProduct.objects.filter(order=order)
    context = {
        'order': order,
        'order_products': order_products,
    }
    return render(request, 'order_detail.html', context)