from django.urls import path
from carts.views import cart,add_cart,remove_cart,remove_cart_item,checkout,increase_cart_item

urlpatterns = [
    path('',cart, name='cart'), 
    path('add_cart/<int:product_id>/', add_cart, name='add_cart'),
    # আপনার carts/urls.py ফাইলে এই দুটো লাইন আপডেট করুন
    path('remove_cart/<int:product_id>/<int:cart_item_id>/', remove_cart, name='remove_cart'),
    path('remove_cart_item/<int:product_id>/<int:cart_item_id>/',remove_cart_item, name='remove_cart_item'),
    # আগের ইউআরএলগুলোর নিচে এটি যোগ করুন
    path('increase_cart_item/<int:product_id>/<int:cart_item_id>/',increase_cart_item, name='increase_cart_item'),
    path('checkout/', checkout, name='checkout'),

]