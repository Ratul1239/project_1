from django.urls import path
# store ইমপোর্ট বাদ দেওয়া হয়েছে
from store.views import home, product_detail, search, add_product, manage_products, edit_product, delete_product

urlpatterns = [
    # হোমপেজ এবং মেনুবারের ক্যাটাগরি ফিল্টার
    path('', home, name='home'),
    path('category/<slug:category_slug>/', home, name='products_by_category'),
    
    path('search/', search, name='search'),
    path('add-product/', add_product, name='add_product'),
    path('manage-products/', manage_products, name='manage_products'),
    path('edit-product/<int:product_id>/', edit_product, name='edit_product'),
    path('delete-product/<int:product_id>/', delete_product, name='delete_product'),
    
    path('<slug:category_slug>/<slug:product_slug>/', product_detail, name='product_detail'),
]