from django.shortcuts import render, redirect
from store.models import Cart, CartItem
from carts.views import _cart_id
from orders.forms import OrderForm
from orders.models import Order, OrderProduct 
from store.models import Product
from django.contrib import admin
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
            data.save() # অর্ডার সেভ হওয়ার সাথে সাথে একটি data.id তৈরি হবে

            # ২. কার্টের সবগুলো আইটেম OrderProduct টেবিলে সেভ করা এবং স্টক কমানো
            for item in cart_items:
                order_product = OrderProduct()
                order_product.order_id = data.id
                order_product.product_id = item.product_id
                order_product.quantity = item.quantity
                order_product.product_price = item.product.price
                order_product.save()

                # --------- নতুন কোড: স্টক আপডেট করা ---------
                product = Product.objects.get(id=item.product_id)
                product.stock -= item.quantity # মূল স্টক থেকে কার্টের পরিমাণ বিয়োগ করা হলো
                product.save()
                # ---------------------------------------------

            # ৩. অর্ডার করা শেষ, তাই কার্ট ক্লিয়ার বা ফাঁকা করে দেওয়া
            CartItem.objects.filter(cart=cart).delete()

            # ৪. সফলভাবে অর্ডার হওয়ার পর Thank You পেজে পাঠিয়ে দেওয়া
            return redirect('order_complete')
    else:
        return redirect('checkout')

# অর্ডার কমপ্লিট হওয়ার পেজ দেখানোর ফাংশন
def order_complete(request):
    return render(request, 'order_complete.html')


# ১. OrderProduct-কে Order এর ভেতরে টেবিল আকারে দেখানোর জন্য
class OrderProductInline(admin.TabularInline):
    model = OrderProduct
    extra = 0
    # কাস্টমার যা অর্ডার করেছে তা যেন ভুলে এডিট না হয়ে যায়, তাই রিড-অনলি করে দেওয়া হলো
    readonly_fields = ('product', 'quantity', 'product_price')

# ২. Order প্যানেলটিকে আরও সুন্দর করে সাজানোর জন্য
class OrderAdmin(admin.ModelAdmin):
    # অর্ডারের লিস্ট পেজে কোন কোন কলাম দেখাবে
    list_display = ['first_name', 'phone', 'email', 'city', 'order_total', 'status', 'created_at']
    # ডানপাশে ফিল্টার করার অপশন
    list_filter = ['status', 'created_at']
    # উপরে সার্চ করার অপশন
    search_fields = ['first_name', 'phone', 'email']
    # ওই ইনলাইন টেবিলটিকে এখানে যুক্ত করে দেওয়া হলো
    inlines = [OrderProductInline]




# শুধুমাত্র অ্যাডমিনরা যেন এই পেজটি দেখতে পারে
@login_required(login_url='/admin/login/') 
def custom_dashboard(request):
    # যদি সাধারণ ইউজার লিংকে ঢোকার চেষ্টা করে, তাকে হোমে পাঠিয়ে দিবে
    if not request.user.is_superuser:
        return redirect('home')
    
    # ডেটাবেস থেকে সব অর্ডারগুলো নিয়ে আসা (নতুন অর্ডার আগে দেখাবে)
    orders = Order.objects.all().order_by('-created_at')
    
    return render(request, 'dashboard.html', {'orders': orders})