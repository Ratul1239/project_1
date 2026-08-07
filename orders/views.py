from django.shortcuts import render, redirect, get_object_or_404
from store.models import Cart, CartItem, Product
from carts.views import _cart_id
from orders.forms import OrderForm
from orders.models import Order, OrderProduct
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Sum
from datetime import timedelta
from django.db.models.functions import TruncDate

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

                # --------- ভুল ঠিক করা হয়েছে (Variation এর বদলে variations) ---------
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
            # ফর্ম ইনভ্যালিড হলে টার্মিনালে এরর প্রিন্ট করবে এবং কার্টে ফেরত পাঠাবে
            print("Form Errors:", form.errors) 
            return redirect('cart') 
            
    else:
        return redirect('cart')

def order_complete(request):
    return render(request, 'order_complete.html')

@login_required(login_url='/admin/login/')
def custom_dashboard(request):
  if not request.user.is_superuser:
    return redirect('home')

  today = timezone.now().date()

  # --- ১. কার্ডের জন্য অর্ডার ও সেলসের হিসাব ---
  total_orders = Order.objects.count()
  today_orders = Order.objects.filter(created_at__date=today).count()

  # Sum ব্যবহার করে টোটাল সেলস বের করা
  total_sales = (
      Order.objects.aggregate(Sum('order_total'))['order_total__sum'] or 0
  )
  today_sales = (
      Order.objects.filter(created_at__date=today).aggregate(
          Sum('order_total')
      )['order_total__sum']
      or 0
  )

  # --- ২. ফিল্টার করার লজিক ---
  filter_by = request.GET.get('filter')

  if filter_by == 'today':
    orders = Order.objects.filter(created_at__date=today).order_by('-created_at')
  elif filter_by == 'all':
    orders = Order.objects.all().order_by('-created_at')
  else:
    # ডিফল্টভাবে কোনো অর্ডার দেখাবে না (লিস্ট হাইড থাকবে)
    orders = []

  # --- ৩. গ্রাফের জন্য গত ৭ দিনের ডেটা তৈরি (অপ্টিমাইজড কুয়েরি) ---
  start_date = today - timedelta(days=6)

  # একসাথে গত ৭ দিনের ডেটা ডাটাবেজ থেকে নিয়ে আসা (N+1 কুয়েরি সমস্যা দূর করতে)
  orders_in_range = (
      Order.objects.filter(
          created_at__date__gte=start_date, created_at__date__lte=today
      )
      .annotate(date=TruncDate('created_at'))
      .values('date')
      .annotate(total=Sum('order_total'))
  )

  # ডেট অনুযায়ী ডিকশনারিতে রূপান্তর করা
  sales_dict = {item['date']: item['total'] for item in orders_in_range}

  labels = []
  sales_data = []

  for i in range(6, -1, -1):
    day = today - timedelta(days=i)
    labels.append(day.strftime('%d %b'))  # যেমন: 05 Aug

    # ডিকশনারি থেকে ওই দিনের সেলস নেওয়া, না থাকলে 0 হবে
    daily_total = sales_dict.get(day, 0)
    sales_data.append(float(daily_total))

  context = {
      'orders': orders,
      'total_orders': total_orders,
      'today_orders': today_orders,
      'total_sales': total_sales,
      'today_sales': today_sales,
      'labels': labels,
      'sales_data': sales_data,
      'filter_by': filter_by,
  }
  return render(request, 'dashboard.html', context)

def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order_products = OrderProduct.objects.filter(order=order)
    context = {
        'order': order,
        'order_products': order_products,
    }
    return render(request, 'order_detail.html', context)